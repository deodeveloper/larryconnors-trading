"""Recent-session signal scanning using the shared book strategy rules."""

from dataclasses import dataclass
from pathlib import Path
import json
import pandas as pd
import plotly.express as px
from .alpaca_sdk import AlpacaDailyData, normalize_symbols
from .data import calendar, load_aux
from .strategies import catalog, resolve, generate
from .execution import limit_fill
from .plotting import dark_theme

VOL_IDS = {
    "buy_fear.vol_panics",
    "buy_fear.vxx_trend",
    "short_term.vix",
    "blocked.vix_stretches",
}


def scan_clock(as_of=None, lookback=4):
    if not isinstance(lookback, int) or not 1 <= lookback <= 60:
        raise ValueError(
            "lookback must be 1..60 trading sessions (4 = latest plus previous 3)"
        )
    now = (
        pd.Timestamp.now(tz="America/New_York")
        if as_of is None
        else pd.Timestamp(as_of)
    )
    if now.tz is None:
        raise ValueError("as_of must include a timezone")
    now = now.tz_convert("America/New_York")
    day = now.tz_localize(None).normalize()
    cal = calendar(day - pd.Timedelta(days=150), day)
    dates = cal.sessions_in_range(day - pd.Timedelta(days=150), day).tz_localize(None)
    target = dates[-1]
    row = cal.schedule.loc[target]
    state = "completed"
    if target == day:
        state = (
            "not_open"
            if now < row["open"]
            else (
                "provisional"
                if now < row["close"] + pd.Timedelta(minutes=15)
                else "completed"
            )
        )
    return now, dates[-lookback:], state


def recent_signals(spec, params, bars, entry, exit, lookback=4, *, provisional=False):
    """Evaluate recent setups independently under source-close assumptions.

    Active means a hypothetical eligible entry has no later exit, not a holding
    in an actual account. Repeated setups are retained, not combined into fills.
    """
    kind = spec["id"].split(".")[1]
    n = len(bars)
    last = n - 1
    events = []
    # Include older candidates to find scheduled exits inside the scan window.
    begin = max(0, n - lookback - (6 if kind in ("ten_day", "overnight") else 0))
    for i in range(begin, n):
        if not bool(entry.iloc[i]):
            continue
        fill_i = i
        price = float(bars.close.iloc[i])
        state = "active"
        exit_i = None
        limit = None
        if kind in ("crash", "new_highs"):
            direction = 1 if spec["direction"] == "long" else -1
            limit = price * (1 - params["limit_pct"] * direction)
            if i == last:
                state = "pending_next_session_limit"
                fill_i = None
                price = None
            else:
                fill_i = i + 1
                b = bars.iloc[fill_i]
                price = limit_fill(b.open, b.high, b.low, limit, direction)
                if price is None:
                    state = (
                        "pending_intraday_limit"
                        if provisional and fill_i == last
                        else "expired_unfilled"
                    )
                    fill_i = None
        if fill_i is not None:
            candidates = [j for j in range(fill_i, n) if bool(exit.iloc[j])]
            due = i + 1 if kind == "overnight" else (i + 5 if kind == "ten_day" else n)
            if due < n:
                candidates.append(due)
            if candidates:
                exit_i = min(candidates)
                state = "exited"
            if provisional and fill_i == last and state == "active":
                state = "provisional_active"
        if i >= n - lookback or (exit_i is not None and exit_i >= n - lookback):
            events.append(
                dict(
                    signal_date=bars.index[i].date().isoformat(),
                    age_sessions=last - i,
                    state=state,
                    fill_date=(
                        None
                        if fill_i is None
                        else bars.index[fill_i].date().isoformat()
                    ),
                    assumed_fill_price=price,
                    limit_price=limit,
                    exit_date=(
                        None
                        if exit_i is None
                        else bars.index[exit_i].date().isoformat()
                    ),
                    exit_phase="open" if kind == "overnight" else "close",
                    recent_entry=i >= n - lookback,
                )
            )
    active = [
        e
        for e in events
        if e["recent_entry"] and e["state"] in ("active", "provisional_active")
    ]
    recent_exits = sorted(
        set(
            [
                bars.index[j].date().isoformat()
                for j in range(max(0, n - lookback), n)
                if bool(exit.iloc[j])
            ]
            + [
                e["exit_date"]
                for e in events
                if e["exit_date"] is not None
                and pd.Timestamp(e["exit_date"]) >= bars.index[max(0, n - lookback)]
            ]
        )
    )
    return (
        dict(
            entry_now=bool(entry.iloc[-1]),
            exit_now=bars.index[-1].date().isoformat() in recent_exits,
            active_recent_entry=bool(active),
            active_entry_dates=[e["signal_date"] for e in active],
            entry_age_sessions=min((e["age_sessions"] for e in active), default=None),
            recent_exit_dates=recent_exits,
            pending_limit=any(e["state"].startswith("pending") for e in events),
        ),
        events,
    )


@dataclass
class ScanResult:
    summary: pd.DataFrame
    events: pd.DataFrame
    metadata: dict

    def save(self, folder):
        folder = Path(folder)
        folder.mkdir(parents=True, exist_ok=True)
        self.summary.to_csv(folder / "signals.csv", index=False)
        self.events.to_csv(folder / "events.csv", index=False)
        (folder / "metadata.json").write_text(
            json.dumps(self.metadata, indent=2, default=str)
        )
        return folder


def show_scan(result):
    from IPython.display import display, Markdown

    display(
        Markdown(
            f"**Target session:** {result.metadata['target_session']} · **Session state:** {result.metadata['session_state']} · **Window:** {result.metadata['lookback']} trading sessions"
        )
    )
    s = result.summary
    if s.empty:
        display(Markdown("No strategies selected."))
        return
    for title, mask in [
        ("Entry conditions now", s.entry_now.eq(True)),
        ("Recent entries without a subsequent exit", s.active_recent_entry.eq(True)),
        ("Exit conditions now", s.exit_now.eq(True)),
        ("Pending next-day / intraday limits", s.pending_limit.eq(True)),
        ("Unavailable, blocked or excluded", s.status.ne("ok")),
    ]:
        display(Markdown("### " + title))
        columns = [
            "symbol",
            "reference_symbol",
            "name",
            "strategy",
            "direction",
            "data_session",
            "session_state",
            "entry_age_sessions",
            "active_entry_dates",
            "recent_exit_dates",
            "reason",
        ]
        display(s.loc[mask, columns])
    display(Markdown("### All evaluated strategies"))
    display(
        s[
            [
                "symbol",
                "reference_symbol",
                "strategy",
                "direction",
                "readiness",
                "status",
                "entry_now",
                "active_recent_entry",
                "exit_now",
                "pending_limit",
            ]
        ]
    )
    ok = s[s.status.eq("ok")]
    if len(ok):
        chart = ok.assign(
            entry=ok.entry_now.astype(int),
            active=ok.active_recent_entry.astype(int),
            exit=ok.exit_now.astype(int),
        )
        counts = (
            chart.groupby("symbol")[["entry", "active", "exit"]]
            .sum()
            .reset_index()
            .melt(id_vars="symbol", var_name="signal", value_name="count")
        )
        dark_theme(
            px.bar(
                counts,
                x="symbol",
                y="count",
                color="signal",
                barmode="group",
                title="Strategy/variant matches (variants may overlap)",
            )
        ).show()


class StrategyScanner:
    def __init__(
        self,
        client,
        *,
        feed="iex",
        cache=".cache/scanner",
        allow_experimental=False,
        include_variants=True,
    ):
        self.data = AlpacaDailyData(client, cache)
        self.feed = feed
        self.allow_experimental = allow_experimental
        self.include_variants = include_variants

    def scan_core_etfs(self, **kwargs):
        return self.scan(["SPY", "QQQ", "SOXX", "GLD"], **kwargs)

    def scan_volatility(self, *, vix_csv=None, **kwargs):
        """VXX trades plus VIX-conditioned SPY trades; VIX is never proxied."""
        return self.scan(["VXX", "VIX"], vix_csv=vix_csv, _volatility=True, **kwargs)

    def scan(
        self,
        symbols,
        *,
        lookback=4,
        as_of=None,
        vix_csv=None,
        trin_csv=None,
        _volatility=False,
    ):
        symbols = normalize_symbols(symbols)
        now, window, session_state = scan_clock(as_of, lookback)
        if (
            session_state == "provisional"
            and now.date() != pd.Timestamp.now(tz="America/New_York").date()
        ):
            raise ValueError(
                "Historical intraday snapshots cannot be reconstructed from completed daily bars; choose a completed-session as_of"
            )
        if now > pd.Timestamp.now(tz="America/New_York") + pd.Timedelta(minutes=1):
            raise ValueError("as_of cannot be in the future")
        target = window[-1]
        rows = []
        all_events = []
        data_quality = {}
        fetched = {}
        errors = {}
        cat = catalog()
        specs = {s["id"]: s for s in cat["strategies"]}
        names = list(specs)
        if self.include_variants:
            names += [v for v in cat["variants"] if v not in specs]

        def get_data(symbol):
            if symbol in errors:
                raise ValueError(errors[symbol])
            if symbol not in fetched:
                if session_state == "not_open":
                    raise ValueError(
                        "Today's session has not opened; no current daily bar. Run after the open or use an earlier completed-session as_of."
                    )
                try:
                    b, q = self.data.load(
                        symbol,
                        str(window[0].date()),
                        str(target.date()),
                        feed=self.feed,
                        refresh=True,
                        as_of=now,
                    )
                except (ValueError, RuntimeError) as error:
                    errors[symbol] = str(error)
                    raise
                fetched[symbol] = b
                data_quality[symbol] = q
            return fetched[symbol]

        for requested in symbols:
            for name in names:
                spec = specs[cat["variants"].get(name, {}).get("strategy", name)]
                sid = spec["id"]
                if _volatility:
                    if requested == "VXX" and sid not in {
                        "buy_fear.vol_panics",
                        "buy_fear.vxx_trend",
                    }:
                        continue
                    if requested == "VIX" and sid not in {
                        "short_term.vix",
                        "blocked.vix_stretches",
                    }:
                        continue
                elif sid in VOL_IDS:
                    continue
                symbol = "SPY" if requested == "VIX" else requested
                base = dict(
                    symbol=symbol,
                    reference_symbol=requested,
                    strategy=name,
                    name=spec.get("name", sid),
                    book=sid.split(".")[0],
                    direction=spec.get("direction"),
                    readiness=spec["status"],
                    target_session=str(target.date()),
                    data_session=None,
                    session_state=session_state,
                    entry_now=False,
                    exit_now=False,
                    active_recent_entry=False,
                    active_entry_dates=[],
                    entry_age_sessions=None,
                    recent_exit_dates=[],
                    pending_limit=False,
                    status="ok",
                    reason="",
                    universe_note=spec.get("universe", "")
                    + " | User-selected-symbol application; original universe membership is not verified.",
                    sources=json.dumps(spec.get("sources", [])),
                    parameters=None,
                    assumptions=json.dumps(spec.get("assumptions", [])),
                )
                try:
                    if not _volatility and requested in ("VIX", "VXX", "^VIX"):
                        raise ValueError(
                            "Use scan_volatility() for VIX/VXX; excluded from general-symbol scanning"
                        )
                    spec, p = resolve(name, allow_experimental=self.allow_experimental)
                    base["parameters"] = json.dumps(p, sort_keys=True)
                    aux = None
                    if sid in ("short_term.vix", "short_term.trin"):
                        path = vix_csv if sid == "short_term.vix" else trin_csv
                        if not path:
                            raise ValueError(
                                "Actual "
                                + ("VIX" if sid == "short_term.vix" else "TRIN")
                                + " CSV required; no proxy substitution"
                            )
                        aux = load_aux(path)
                        needed = (
                            ["open", "close"] if sid == "short_term.vix" else ["close"]
                        )
                        if any(c not in aux for c in needed):
                            raise ValueError(
                                "Auxiliary CSV requires columns: " + ", ".join(needed)
                            )
                        if (
                            aux[needed].isna().any().any()
                            or (aux[needed] <= 0).any().any()
                        ):
                            raise ValueError(
                                "Auxiliary data has missing/nonpositive values"
                            )
                    bars = get_data(symbol)
                    if aux is not None:
                        bars = bars.loc[bars.index >= aux.index.min()]
                        if (bars.index < window[0]).sum() < 300:
                            raise ValueError(
                                "Auxiliary data needs at least 300 warm-up sessions before scan window"
                            )
                        aligned = aux.reindex(bars.index)
                        if aligned[needed].isna().any().any():
                            raise ValueError(
                                "Auxiliary CSV missing required sessions, including target; refresh the actual index data"
                            )
                        aux = aligned
                    _, entry, exit = generate(spec, bars, p, aux)
                    values, events = recent_signals(
                        spec,
                        p,
                        bars,
                        entry,
                        exit,
                        lookback,
                        provisional=session_state == "provisional",
                    )
                    base.update(values, data_session=str(bars.index[-1].date()))
                    for e in events:
                        all_events.append(
                            dict(
                                symbol=symbol,
                                reference_symbol=requested,
                                strategy=name,
                                **e,
                            )
                        )
                except (ValueError, RuntimeError, FileNotFoundError) as error:
                    base.update(status="unavailable", reason=str(error))
                rows.append(base)
        metadata = dict(
            as_of=now.isoformat(),
            target_session=str(target.date()),
            session_state=session_state,
            lookback=lookback,
            window=[str(x.date()) for x in window],
            symbols=symbols,
            feed=self.feed,
            allow_experimental=self.allow_experimental,
            include_variants=self.include_variants,
            data_quality=data_quality,
            auxiliary_inputs=dict(
                vix_csv=str(vix_csv) if vix_csv else None,
                trin_csv=str(trin_csv) if trin_csv else None,
            ),
            conventions="Source-close hypothetical setups, no account positions/cash/borrow/scale-ins. Intraday signals provisional. Limit fill is OHLC touch assumption; no queue model. No exit since recent setup is not proof of a real holding.",
        )
        return ScanResult(pd.DataFrame(rows), pd.DataFrame(all_events), metadata)
