"""Official Alpaca SDK adapter for the book notebooks."""

import hashlib
import json
import os
from pathlib import Path
import time

import pandas as pd
import requests
from alpaca.common.exceptions import APIError
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.enums import Adjustment, DataFeed
from .data import warmup_start, validate


def read_notebook_secret(name, *, prompt=True):
    """Read environment or Colab Secrets, then optionally prompt without echo."""
    aliases = {"API_KEY": "APCA_API_KEY_ID", "API_SECRET": "APCA_API_SECRET_KEY"}
    value = os.environ.get(name) or os.environ.get(aliases.get(name, name))
    if not value:
        try:
            from google.colab import userdata
        except ImportError:
            pass
        else:
            try:
                value = userdata.get(name)
            except (userdata.SecretNotFoundError, userdata.NotebookAccessError):
                pass
    if not value and prompt:
        from getpass import getpass

        value = getpass(f"{name} (hidden; kept only in runtime memory): ")
    if not value:
        raise ValueError(
            f"Set {name} in environment/Colab Secrets or enter it at the prompt"
        )
    return value


def normalize_symbols(symbols):
    if isinstance(symbols, str):
        symbols = [symbols]
    if not isinstance(symbols, (list, tuple)) or not symbols:
        raise ValueError("symbols must be a ticker or a non-empty list of tickers")
    cleaned = []
    for symbol in symbols:
        if not isinstance(symbol, str) or not symbol.strip():
            raise ValueError("Every ticker must be a non-empty string")
        value = symbol.strip().upper()
        if value not in cleaned:
            cleaned.append(value)
    return cleaned


class AlpacaDailyData:
    """Cache complete SDK responses by symbol, range, feed and adjustment.

    get_stock_bars performs SDK pagination internally with no result-count limit.
    The application retries transient whole-request failures; credentials never
    enter the cache key, configuration, logs, or exported reports.
    """

    def __init__(self, client: StockHistoricalDataClient, cache=".cache/alpaca_sdk"):
        self.client = client
        self.cache = Path(cache)

    def load(
        self,
        symbol,
        start_date,
        end_date,
        *,
        feed="iex",
        adjustment="split",
        warmup_sessions=600,
        refresh=False,
    ):
        symbol = normalize_symbols(symbol)[0]
        start, end = pd.Timestamp(start_date), pd.Timestamp(end_date)
        if (
            start.tz is not None
            or end.tz is not None
            or start != start.normalize()
            or end != end.normalize()
        ):
            raise ValueError("Use timezone-free YYYY-MM-DD dates")
        if start > end:
            raise ValueError("start_date must be on or before end_date")
        if warmup_sessions < 300:
            raise ValueError("At least 300 warm-up sessions required; default 600")
        if adjustment not in ("split", "all"):
            raise ValueError(
                "Use split or all adjusted research prices; raw corporate-action accounting is unsupported"
            )
        first = warmup_start(start_date, warmup_sessions)
        request_key = dict(
            symbol=symbol,
            start=first,
            end=str(end.date()),
            feed=feed,
            adjustment=adjustment,
            timeframe="1Day",
            adapter="alpaca-py-0.44.0",
        )
        key = hashlib.sha256(
            json.dumps(request_key, sort_keys=True).encode()
        ).hexdigest()
        path = self.cache / f"{key}.csv"
        if path.exists() and not refresh:
            bars = pd.read_csv(path, index_col=0, parse_dates=True)
        else:
            request = StockBarsRequest(
                symbol_or_symbols=[symbol],
                timeframe=TimeFrame.Day,
                start=pd.Timestamp(first)
                .tz_localize("America/New_York")
                .to_pydatetime(),
                end=(end + pd.Timedelta(days=1))
                .tz_localize("America/New_York")
                .to_pydatetime(),
                feed=DataFeed(feed),
                adjustment=Adjustment(adjustment),
            )
            for attempt in range(4):
                try:
                    response = self.client.get_stock_bars(request)
                    break
                except APIError as error:
                    if (
                        error.status_code not in (429, 500, 502, 503, 504)
                        or attempt == 3
                    ):
                        raise RuntimeError(
                            f"Alpaca data request failed (HTTP {error.status_code}); check credentials, feed entitlement and dates"
                        ) from None
                    time.sleep(2**attempt)
                except (requests.ConnectionError, requests.Timeout):
                    if attempt == 3:
                        raise RuntimeError(
                            "Alpaca connection failed after retries"
                        ) from None
                    time.sleep(2**attempt)
            frame = response.df
            if (
                frame.empty
                or not isinstance(frame.index, pd.MultiIndex)
                or symbol not in frame.index.get_level_values("symbol")
            ):
                raise ValueError(
                    f"No Alpaca bars for {symbol}; check ticker, dates and feed"
                )
            bars = frame.xs(symbol, level="symbol").copy()
            timestamps = pd.DatetimeIndex(pd.to_datetime(bars.index, utc=True))
            bars.index = (
                timestamps.tz_convert("America/New_York").tz_localize(None).normalize()
            )
            bars = bars.loc[
                (bars.index >= pd.Timestamp(first)) & (bars.index <= end),
                ["open", "high", "low", "close", "volume"],
            ].sort_index()
        # 600 sessions is a download buffer, not an indicator requirement.
        # 300 prior sessions covers SMA200, nested 252-day high + 20-day
        # windows (271 observations), and the fixed ConnorsRSI lookbacks.
        # Only an unavailable leading prefix may be omitted; never bridge gaps.
        requested_quality = validate(bars, first, str(end.date()))
        if bars.empty:
            raise ValueError(f"No Alpaca bars for {symbol} in the requested range")
        available_start = bars.index.min()
        quality = validate(bars, str(available_start.date()), str(end.date()))
        prior_sessions = int((bars.index < start).sum())
        leading_missing = [
            day for day in requested_quality["missing_sessions"]
            if pd.Timestamp(day) < available_start
        ]
        quality.update(
            requested_warmup_sessions=warmup_sessions,
            available_warmup_sessions=prior_sessions,
            minimum_warmup_sessions=300,
            unavailable_leading_sessions=leading_missing,
            actual_data_start=str(available_start.date()),
        )
        if prior_sessions < 300:
            raise ValueError(
                f"{symbol}: insufficient warm-up on {feed}: {prior_sessions} prior "
                f"sessions available; at least 300 required. First bar: "
                f"{available_start.date()}. Choose a later backtest start or an "
                "explicitly selected feed with earlier history; prices are not filled."
            )
        if quality["missing_sessions"] or quality["non_sessions"]:
            raise ValueError(
                f"{symbol}: incomplete history on {feed}: "
                f"{len(quality['missing_sessions'])} missing sessions within "
                f"{available_start.date()} through {end.date()} "
                f"(first missing dates: {quality['missing_sessions'][:5]}); "
                f"{len(quality['non_sessions'])} non-session bars. "
                "Choose completed historical dates, retry with refresh=True, or "
                "explicitly select another feed; prices are not filled."
            )
        if not path.exists() or refresh:
            self.cache.mkdir(parents=True, exist_ok=True)
            temp = path.with_suffix(".tmp")
            bars.to_csv(temp)
            temp.replace(path)
        quality.update(request_key)
        return bars, quality
