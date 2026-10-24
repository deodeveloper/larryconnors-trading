from types import SimpleNamespace
import pandas as pd
import pytest
from connors.scanner import StrategyScanner, scan_clock, recent_signals
from connors.data import synthetic
from connors.strategies import catalog


def sample(kind="hpe.rsi4.long", en=(0,), ex=(), n=8, direction="long", **kwargs):
    dates = pd.bdate_range("2024-01-02", periods=n)
    bars = pd.DataFrame(
        dict(open=100.0, high=101.0, low=99.0, close=100.0, volume=1000.0), index=dates
    )
    entry = pd.Series(False, index=dates)
    exit = pd.Series(False, index=dates)
    entry.iloc[list(en)] = True
    exit.iloc[list(ex)] = True
    return recent_signals(
        {"id": kind, "direction": direction}, kwargs, bars, entry, exit, 4
    )


def test_four_session_window_and_exit_cancels_earlier_entry():
    row, events = sample(en=(3, 4, 5, 7), ex=(6,))
    assert row["active_entry_dates"] == ["2024-01-11"]
    assert row["entry_age_sessions"] == 0
    assert len(events) == 3  # age 4 is excluded
    assert [e["state"] for e in events] == ["exited", "exited", "active"]
    assert row["recent_exit_dates"] == ["2024-01-10"]


def test_exit_on_latest_bar_and_same_bar_precedence():
    row, _ = sample(en=(4, 7), ex=(7,))
    assert row["entry_now"] and row["exit_now"] and not row["active_recent_entry"]


def test_old_exit_does_not_cancel_new_entry_and_age_three_is_included():
    row, _ = sample(en=(4,), ex=(3,))
    assert row["active_recent_entry"] and row["entry_age_sessions"] == 3


def test_scheduled_exits():
    row, _ = sample("short_term.overnight", en=(6, 7))
    assert row["exit_now"] and row["active_entry_dates"] == ["2024-01-11"]
    row, events = sample("short_term.ten_day", en=(2,))
    assert row["exit_now"] and not row["active_recent_entry"]
    assert events[0]["exit_date"] == "2024-01-11"


def test_limit_pending_and_unfilled_never_active():
    row, events = sample("buy_fear.new_highs", en=(5, 7), limit_pct=0.07)
    assert row["entry_now"] and row["pending_limit"] and not row["active_recent_entry"]
    assert [e["state"] for e in events] == [
        "expired_unfilled",
        "pending_next_session_limit",
    ]


def test_limit_open_improvement_and_provisional_order_not_expired():
    b = synthetic(["X"], "2023-01-03", "2023-02-01")["X"].tail(4).copy()
    b.loc[:, "close"] = 100.0
    b.loc[:, "open"] = 90.0
    b.loc[:, "low"] = 89.0
    b.loc[:, "high"] = 101.0
    en = pd.Series([False, False, True, False], index=b.index)
    ex = en & False
    spec = {"id": "buy_fear.new_highs", "direction": "long"}
    row, events = recent_signals(spec, {"limit_pct": 0.07}, b, en, ex)
    assert row["active_recent_entry"] and events[0]["assumed_fill_price"] == 90
    b.loc[:, "low"] = 99.0
    b.loc[:, "open"] = 100.0
    row, events = recent_signals(spec, {"limit_pct": 0.07}, b, en, ex, provisional=True)
    assert row["pending_limit"] and events[0]["state"] == "pending_intraday_limit"


@pytest.mark.parametrize(
    "at,target,state",
    [
        ("2024-07-06T12:00:00-04:00", "2024-07-05", "completed"),
        ("2024-07-04T12:00:00-04:00", "2024-07-03", "completed"),
        ("2024-07-03T12:00:00-04:00", "2024-07-03", "provisional"),
        ("2024-07-03T13:16:00-04:00", "2024-07-03", "completed"),
        ("2024-07-05T08:00:00-04:00", "2024-07-05", "not_open"),
    ],
)
def test_calendar_holidays_weekends_early_close_and_open(at, target, state):
    _, window, actual = scan_clock(at)
    assert len(window) == 4 and str(window[-1].date()) == target and actual == state


class Client:
    def __init__(self):
        self.requests = []

    def get_stock_bars(self, r):
        self.requests.append(r)
        sym = r.symbol_or_symbols[0]
        b = synthetic([sym], r.start.date().isoformat(), r.end.date().isoformat())[sym]
        b.index = b.index.tz_localize("America/New_York").tz_convert("UTC")
        b.index.name = "timestamp"
        return SimpleNamespace(df=pd.concat({sym: b}, names=["symbol"]))


def test_core_etfs_all_books_variants_and_no_volatility(tmp_path):
    client = Client()
    scanner = StrategyScanner(client, cache=tmp_path, allow_experimental=True)
    result = scanner.scan_core_etfs(as_of="2024-12-31T17:00:00-05:00")
    assert {r.symbol_or_symbols[0] for r in client.requests} == {
        "SPY",
        "QQQ",
        "SOXX",
        "GLD",
    }
    assert len(client.requests) == 4
    s = result.summary
    assert not s.strategy.str.contains("vix|vxx|vol_").any()
    assert {"hpe", "short_term", "buy_fear"} <= set(s[s.status == "ok"].book)
    assert "cumulative50" in set(s.strategy)
    allowed = {"short_term.trin"} | {
        x["id"] for x in catalog()["strategies"] if x["status"] == "blocked"
    }
    assert set(s[s.status != "ok"].strategy) <= allowed
    assert s[s.status == "ok"].data_session.eq("2024-12-31").all()
    assert all(
        r.end == pd.Timestamp("2024-12-31T22:00:00").to_pydatetime()
        for r in client.requests
    )
    result.save(tmp_path / "export")
    assert (tmp_path / "export/metadata.json").exists()


def test_volatility_vix_is_reference_for_spy_and_requires_actual_index(tmp_path):
    client = Client()
    scanner = StrategyScanner(client, cache=tmp_path)
    result = scanner.scan_volatility(as_of="2024-12-31T17:00:00-05:00")
    assert [r.symbol_or_symbols[0] for r in client.requests] == ["VXX"]
    vix = result.summary.query("reference_symbol == 'VIX'")
    assert set(vix.symbol) == {"SPY"} and vix.status.eq("unavailable").all()
    assert "Actual VIX CSV required" in vix.iloc[0].reason
    v = synthetic(["VIX"], "2021-01-01", "2024-12-31")["VIX"][["open", "close"]]
    file = tmp_path / "vix.csv"
    v.to_csv(file)
    result = scanner.scan_volatility(vix_csv=file, as_of="2024-12-31T17:00:00-05:00")
    assert result.summary.query("strategy == 'short_term.vix'").status.iloc[0] == "ok"
    v.iloc[:-1].to_csv(file)
    result = scanner.scan_volatility(vix_csv=file, as_of="2024-12-31T17:00:00-05:00")
    assert (
        "missing required sessions"
        in result.summary.query("strategy == 'short_term.vix'").reason.iloc[0]
    )


def test_general_scan_rejects_vix_vxx_and_premarket_is_explicit(tmp_path):
    client = Client()
    scanner = StrategyScanner(client, cache=tmp_path)
    r = scanner.scan(["VIX", "VXX"], as_of="2024-12-31T17:00:00-05:00")
    assert client.requests == [] and r.summary.status.eq("unavailable").all()
    r = scanner.scan("spy", as_of="2024-12-31T08:00:00-05:00")
    assert client.requests == [] and r.summary.status.eq("unavailable").all()
    assert r.metadata["target_session"] == "2024-12-31"


def test_data_failure_is_not_no_signal_and_only_fetched_once(tmp_path):
    client = Client()
    scanner = StrategyScanner(client, cache=tmp_path)
    calls = []

    def fail(*a, **kw):
        calls.append(a)
        raise ValueError("missing session")

    scanner.data.load = fail
    r = scanner.scan("SPY", as_of="2024-12-31T17:00:00-05:00")
    assert len(calls) == 1 and r.summary.status.eq("unavailable").all()
