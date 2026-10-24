from types import SimpleNamespace
from pathlib import Path
import json
import numpy as np
import pandas as pd
import pytest
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.timeframe import TimeFrame

from connors.alpaca_sdk import AlpacaDailyData, normalize_symbols, read_notebook_secret
from connors.data import synthetic
from connors.notebook import NotebookResearch, performance_matrix
from connors.notebook_strategies import (
    PositionType,
    rsi_sma_strategy,
    tps_strategy,
    double_seven_strategy,
    terror_gaps_strategy,
    vix_rsi_strategy,
    vol_panics_strategy,
)


class FakeClient:
    def __init__(self):
        self.requests = []

    def get_stock_bars(self, request):
        self.requests.append(request)
        symbol = request.symbol_or_symbols[0]
        frame = synthetic([symbol], request.start.date().isoformat(), "2023-12-29")[
            symbol
        ]
        frame.index = frame.index.tz_localize("America/New_York").tz_convert("UTC")
        frame.index.name = "timestamp"
        return SimpleNamespace(df=pd.concat({symbol: frame}, names=["symbol"]))


def test_normalizes_single_ticker_and_list():
    assert normalize_symbols(" spy ") == ["SPY"]
    assert normalize_symbols(["spy", "QQQ", "SPY"]) == ["SPY", "QQQ"]
    with pytest.raises(ValueError):
        normalize_symbols([])


def test_sdk_cache_request_and_warmup(tmp_path):
    client = FakeClient()
    data = AlpacaDailyData(client, tmp_path)
    bars, quality = data.load("spy", "2022-01-03", "2023-12-29")
    assert len(client.requests) == 1
    request = client.requests[0]
    assert request.timeframe.value == TimeFrame.Day.value
    assert request.limit is None
    assert request.start.year < 2022
    assert request.feed.value == "iex"
    data.load("SPY", "2022-01-03", "2023-12-29")
    assert len(client.requests) == 1
    assert not quality["missing_sessions"]
    assert bars.index.tz is None


def test_real_sdk_paginates_with_no_truncation(monkeypatch):
    client = StockHistoricalDataClient("FAKE_KEY", "FAKE_SECRET")
    seen = []
    bar = dict(
        t="2022-01-03T05:00:00Z", o=100, h=101, l=99, c=100, v=1000, n=20, vw=100
    )

    def get(path, data):
        seen.append(dict(data))
        if len(seen) == 1:
            return {"bars": {"SPY": [bar]}, "next_page_token": "page2"}
        return {
            "bars": {"SPY": [{**bar, "t": "2022-01-04T05:00:00Z"}]},
            "next_page_token": None,
        }

    monkeypatch.setattr(client, "get", get)
    from alpaca.data.requests import StockBarsRequest

    result = client.get_stock_bars(
        StockBarsRequest(symbol_or_symbols=["SPY"], timeframe=TimeFrame.Day)
    )
    assert len(result.df) == 2
    assert seen[1]["page_token"] == "page2"


def test_user_call_shape_returns_each_symbol_and_vectorbt_charts(tmp_path):
    client = FakeClient()
    research = NotebookResearch(
        client, cache=tmp_path / "cache", output=tmp_path / "reports"
    )
    batch = research.plot_all_stocks_pnl_charts(
        ["spy", "qqq"],
        "2022-01-03",
        "2023-12-29",
        position_type=PositionType.LONG,
        position_steps=[0.5, 0.5],
        strategy_func=rsi_sma_strategy,
        show=False,
        save=False,
    )
    assert batch.performance.status.tolist() == ["ok", "ok"]
    assert list(batch.results) == ["SPY", "QQQ"]
    assert batch.results["SPY"].config["execution"]["position_steps"] == [0.5, 0.5]
    for figures in batch.figures.values():
        assert set(figures) == {"trades", "wins_losses", "equity", "drawdown"}
        assert all(fig.to_json() for fig in figures.values())
    assert len(performance_matrix({"run": batch})) == 2
    journal = (tmp_path / "reports/research.jsonl").read_text()
    assert "FAKE_KEY" not in journal


def test_blocked_and_auxiliary_skip_without_fetch(tmp_path):
    client = FakeClient()
    research = NotebookResearch(client, output=tmp_path)
    for strategy in [terror_gaps_strategy, vix_rsi_strategy]:
        result = research.plot_all_stocks_pnl_charts(
            "SPY",
            "2022-01-03",
            "2023-12-29",
            strategy_func=strategy,
            show=False,
            save=False,
        )
        assert result.performance.status.iloc[0] == "skipped"
        assert result.performance.reason.iloc[0]
    assert client.requests == []


def test_no_invented_scale_rules(tmp_path):
    client = FakeClient()
    research = NotebookResearch(client, output=tmp_path)
    batch = research.plot_all_stocks_pnl_charts(
        "SPY",
        "2022-01-03",
        "2023-12-29",
        strategy_func=double_seven_strategy,
        position_steps=[0.5, 0.5],
        show=False,
        save=False,
    )
    assert batch.performance.status.iloc[0] == "skipped"
    assert client.requests == []


def test_tps_sizing_override_is_used_and_labeled(tmp_path):
    research = NotebookResearch(
        FakeClient(), cache=tmp_path / "cache", output=tmp_path / "reports"
    )
    batch = research.plot_all_stocks_pnl_charts(
        "SPY",
        "2022-01-03",
        "2023-12-29",
        strategy_func=tps_strategy,
        position_steps=[0.25] * 4,
        show=False,
        save=False,
    )
    assert batch.performance.status.iloc[0] == "ok"
    assert "sizing experiment" in batch.performance.note.iloc[0]
    cfg = batch.results["SPY"].config
    assert cfg["execution"]["position_steps"] == [0.25] * 4


def test_credentials_new_names_and_no_echo(monkeypatch, capsys):
    monkeypatch.setenv("API_KEY", "ONLY_A_TEST")
    assert read_notebook_secret("API_KEY", prompt=False) == "ONLY_A_TEST"
    assert capsys.readouterr().out == ""


def test_three_notebooks_have_all_primary_sections_and_clean_cells():
    import nbformat

    books = [
        ("high_probability_etf_trading", 7),
        ("short_term_trading_strategies", 8),
        ("buy_the_fear_sell_the_greed", 7),
    ]
    for filename, count in books:
        notebook = nbformat.read(Path("notebooks") / f"{filename}.ipynb", as_version=4)
        nbformat.validate(notebook)
        text = "\n".join(cell.source for cell in notebook.cells)
        assert "API_KEY" in text and "API_SECRET" in text
        assert "StockHistoricalDataClient" in text and "TimeFrame" in text
        assert text.count("strategy_start_date = start_date") >= count
        assert "performance_matrix(results)" in text
        for cell in notebook.cells:
            if cell.cell_type == "code":
                compile(cell.source, filename, "exec")
                assert not cell.outputs and cell.execution_count is None


def test_transient_sdk_failure_retries(monkeypatch, tmp_path):
    import requests
    from connors import alpaca_sdk

    client = FakeClient()
    original = client.get_stock_bars
    calls = []

    def flaky(request):
        calls.append(request)
        if len(calls) == 1:
            raise requests.ConnectionError("temporary")
        return original(request)

    monkeypatch.setattr(client, "get_stock_bars", flaky)
    monkeypatch.setattr(alpaca_sdk.time, "sleep", lambda _: None)
    bars, _ = AlpacaDailyData(client, tmp_path).load("SPY", "2022-01-03", "2023-12-29")
    assert len(calls) == 2 and not bars.empty


def test_rendered_performance_table_and_no_trade_plots(tmp_path, monkeypatch):
    from connors.notebook import display_performance_matrix

    client = FakeClient()
    original = client.get_stock_bars

    def flat(request):
        response = original(request)
        for column in ["open", "high", "low", "close"]:
            response.df[column] = 100.0
        return response

    monkeypatch.setattr(client, "get_stock_bars", flat)
    research = NotebookResearch(
        client, cache=tmp_path / "cache", output=tmp_path / "reports"
    )
    batch = research.plot_all_stocks_pnl_charts(
        "SPY",
        "2022-01-03",
        "2023-12-29",
        strategy_func=rsi_sma_strategy,
        show=False,
        save=False,
    )
    assert batch.performance.status.iloc[0] == "ok"
    assert batch.performance.completed_episodes.iloc[0] == 0
    assert batch.performance.total_return.iloc[0] == 0
    # Render the same Styler needed by the notebook, catching optional dependencies.
    assert "<table" in batch.performance.style.format(na_rep="—").to_html()


def test_notebook_strategy_names_are_book_headings_not_nested_rule_numbers():
    from connors.strategies import catalog

    mapping = {item["id"]: item for item in catalog()["strategies"]}
    assert mapping["short_term.vix"]["name"] == "VIX RSI Strategy"
    assert mapping["short_term.trin"]["name"] == "TRIN Strategy"
    assert mapping["short_term.cumulative"]["rules"].startswith("2. Cumulative RSI")
    assert "35" in mapping["short_term.cumulative"]["rules"]
    assert "50" in mapping["short_term.cumulative"]["rules"]
