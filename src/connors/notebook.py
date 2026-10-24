"""A one-call notebook interface over the shared strategy and vectorbt engine."""

from dataclasses import dataclass, field
from pathlib import Path
import json
import hashlib
import numpy as np
import pandas as pd
import plotly.express as px

from .alpaca_sdk import AlpacaDailyData, normalize_symbols
from .data import load_aux
from .execution import run
from .notebook_strategies import BookStrategy, PositionType
from .reporting import daily_equity, episodes, metrics, export
from .plotting import dark_theme
from .research import record
from .strategies import stages


@dataclass
class NotebookBatch:
    performance: pd.DataFrame
    results: dict = field(default_factory=dict)
    figures: dict = field(default_factory=dict)


def _position_parameters(spec, parameters, steps):
    parameters = dict(parameters)
    if steps is None:
        return parameters, None, None
    steps = [float(value) for value in steps]
    if (
        not steps
        or not all(np.isfinite(value) and value > 0 for value in steps)
        or not np.isclose(sum(steps), 1)
    ):
        raise ValueError(
            "position_steps must be positive fractions summing to 1, e.g. [0.5, 0.5]"
        )
    kind = spec["id"].split(".")[1]
    if kind in ("high_low", "rsi4", "r3", "percent_b", "multiple_days"):
        parameters["aggressive"] = len(steps) > 1
    if kind == "vol_panics":
        if len(steps) > 4:
            raise ValueError("Vol Panics supports at most four stages")
        canonical = {
            1: [1.0],
            2: [0.5, 0.5],
            3: [0.2, 0.3, 0.5],
            4: [0.1, 0.2, 0.3, 0.4],
        }
        parameters.update(stages=canonical[len(steps)], equal_units=len(steps) == 2)
    baseline, equal_units = stages(spec, parameters)
    if len(steps) > len(baseline):
        raise ValueError(
            f"{spec['id']} defines at most {len(baseline)} stages; no invented additions"
        )
    if equal_units and len(steps) > 1 and len(set(steps)) != 1:
        raise ValueError(
            "This source strategy uses equal-share units. Use equal position_steps; unequal-unit experiments need a separate specification."
        )
    note = (
        None
        if steps == baseline
        else f"User sizing experiment: {steps}; source baseline {baseline}"
    )
    return parameters, steps, note


def _make_figures(result):
    symbol = next(iter(result.bars))
    pf = result.portfolio
    # Positions aggregate scale-ins into one episode; entry trades would overcount them.
    positions = pf.positions.regroup(False)[symbol].closed
    trade_chart = positions.plot()
    trade_chart.update_layout(
        title=f"{symbol} — completed trades: green wins / red losses"
    )
    pnl_chart = positions.plot_pnl()
    pnl_chart.update_layout(title=f"{symbol} — completed position P&L (vectorbt)")
    eq = daily_equity(result)
    initial = result.config["execution"]["initial_capital"]
    curves = pd.DataFrame(
        {
            "equity": eq.combined,
            "drawdown": eq.combined / eq.combined.cummax().clip(lower=initial) - 1,
        }
    )
    figures = {
        "trades": trade_chart,
        "wins_losses": pnl_chart,
        "equity": px.line(
            curves, y="equity", title=f"{symbol} — daily equity after costs"
        ),
        "drawdown": px.area(curves, y="drawdown", title=f"{symbol} — daily drawdown"),
    }

    return {name: dark_theme(figure) for name, figure in figures.items()}


class NotebookResearch:
    def __init__(
        self,
        client,
        *,
        cache=".cache/alpaca_sdk",
        output="reports/notebooks",
        feed="iex",
        adjustment="split",
        initial_capital=100000,
        fees=0.0005,
        slippage=0.0005,
        execution_mode="source_close",
        assume_borrow_available=False,
        borrow_rate=0.0,
    ):
        self.data = AlpacaDailyData(client, cache)
        self.output = Path(output)
        self.feed, self.adjustment = feed, adjustment
        self.execution = dict(
            initial_capital=initial_capital,
            fees=fees,
            slippage=slippage,
            mode=execution_mode,
            assume_borrow_available=assume_borrow_available,
            borrow_rate=borrow_rate,
            shared_cash=True,
            position_fraction=0.95,
            max_gross_exposure=1.0,
            max_leverage=1.0,
        )

    def plot_all_stocks_pnl_charts(
        self,
        symbols,
        start_date,
        end_date,
        *,
        strategy_func: BookStrategy,
        position_type=PositionType.LONG,
        position_steps=None,
        strategy_name=None,
        variant=None,
        parameters=None,
        allow_experimental=False,
        auxiliary_csv=None,
        execution_mode=None,
        position_fraction=0.95,
        show=True,
        save=True,
        refresh=False,
    ):
        """Run a book strategy for each ticker and return plots, matrix and portfolios.

        Each ticker receives independent initial capital. No trades are submitted.
        Missing data or blocked specifications produce explicit status rows so
        Run All can continue to the remaining documented strategies.
        """
        if not isinstance(strategy_func, BookStrategy):
            raise TypeError(
                "strategy_func must be a named book strategy from connors.notebook_strategies"
            )
        symbols = normalize_symbols(symbols)
        direction = PositionType(position_type)
        name = strategy_name or strategy_func.name
        rows, results, figures = [], {}, {}
        for symbol in symbols:
            cfg = {
                "strategy": variant
                or (
                    strategy_func.long_id
                    if direction == PositionType.LONG
                    else strategy_func.short_id
                ),
                "data": dict(
                    provider="alpaca_sdk",
                    symbols=[symbol],
                    start=str(start_date),
                    end=str(end_date),
                    feed=self.feed,
                    adjustment=self.adjustment,
                    universe="user-selected ticker; not an automatic index proxy",
                ),
                "execution": {
                    **self.execution,
                    "position_fraction": position_fraction,
                    "mode": execution_mode or self.execution["mode"],
                },
                "parameters": dict(parameters or {}),
                "allow_experimental": allow_experimental,
                "auxiliary_csv": str(auxiliary_csv) if auxiliary_csv else None,
            }
            journal = self.output / "research.jsonl"
            record(cfg, journal, "started")
            try:
                spec, params = strategy_func(
                    direction, parameters, allow_experimental, variant
                )
                params, steps, sizing_note = _position_parameters(
                    spec, params, position_steps
                )
                if steps is not None:
                    cfg["execution"]["position_steps"] = steps
                cfg["parameters"] = params
                cfg["sizing_note"] = sizing_note
                record(cfg, journal, "resolved")
                if (
                    spec["direction"] == "short"
                    and not cfg["execution"]["assume_borrow_available"]
                ):
                    raise ValueError(
                        "Short research requires assume_borrow_available=True in notebook setup"
                    )
                if (
                    spec["id"] in ("short_term.vix", "short_term.trin")
                    and not auxiliary_csv
                ):
                    raise ValueError(
                        "Supply auxiliary_csv with actual VIX/TRIN history. Alpaca stock bars do not provide it; no proxy is substituted."
                    )
                bars, quality = self.data.load(
                    symbol,
                    start_date,
                    end_date,
                    feed=self.feed,
                    adjustment=self.adjustment,
                    refresh=refresh,
                )
                result = run({symbol: bars}, spec, params, cfg, load_aux(auxiliary_csv))
                equity = daily_equity(result).combined
                trades = episodes(result.orders)
                stats = metrics(
                    equity, cfg["execution"]["initial_capital"], trades, result.orders
                )
                row = dict(
                    strategy=name,
                    variant=variant or spec["id"],
                    symbol=symbol,
                    direction=direction.value,
                    start_date=str(start_date),
                    end_date=str(end_date),
                    status="ok",
                    **stats,
                    wins=int((trades.pnl > 0).sum()),
                    losses=int((trades.pnl < 0).sum()),
                    breakeven=int((trades.pnl == 0).sum()),
                    note=sizing_note
                    or (
                        spec.get("reason", "")
                        if spec["status"] == "experimental"
                        else ""
                    ),
                )
                charts = _make_figures(result)
                results[symbol], figures[symbol] = result, charts
                if save:
                    digest = hashlib.sha256(
                        json.dumps(cfg, sort_keys=True).encode()
                    ).hexdigest()[:10]
                    folder = self.output / f"{spec['id']}-{symbol}-{digest}"
                    export(result, folder, {symbol: quality})
                    for key, chart in charts.items():
                        chart.write_html(folder / f"{key}.html", include_plotlyjs=True)
                    row["report"] = str(folder / "report.html")
                rows.append(row)
                record(cfg, journal, "completed")
                if show:
                    from IPython.display import display, Markdown

                    display(
                        Markdown(
                            f"### {name} · {symbol} · {direction.value}\n{start_date} → {end_date}"
                        )
                    )
                    for chart in charts.values():
                        chart.show()
            except (ValueError, RuntimeError, FileNotFoundError) as error:
                row = dict(
                    strategy=name,
                    variant=variant or cfg["strategy"],
                    symbol=symbol,
                    direction=direction.value,
                    start_date=str(start_date),
                    end_date=str(end_date),
                    status="skipped",
                    reason=str(error),
                )
                rows.append(row)
                record(cfg, journal, "skipped: " + type(error).__name__)
                if show:
                    from IPython.display import display, Markdown

                    display(Markdown(f"**{name} · {symbol}: skipped.** {error}"))
        batch = NotebookBatch(pd.DataFrame(rows), results, figures)
        if show:
            display_performance_matrix(batch.performance)
        return batch


def performance_matrix(batches):
    """Concatenate NotebookBatch values, preserving skipped-strategy reasons."""
    items = batches.values() if isinstance(batches, dict) else batches
    frames = [item.performance for item in items if item is not None]
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def display_performance_matrix(frame):
    from IPython.display import display

    if frame.empty:
        display(frame)
        return
    percent_columns = [
        c
        for c in (
            "total_return",
            "cagr",
            "max_drawdown",
            "win_rate",
            "average_trade_return",
        )
        if c in frame
    ]
    styles = {c: "{:.2%}" for c in percent_columns}
    styles.update(
        {
            c: "{:.2f}"
            for c in (
                "sharpe",
                "profit_factor",
                "turnover",
                "mean_holding_calendar_days",
            )
            if c in frame
        }
    )
    display(frame.style.format(styles, na_rep="—"))
