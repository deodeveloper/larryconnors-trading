"""Regenerate the three book workbooks from the source-linked catalog."""

from pathlib import Path
import json
import nbformat as nb

ROOT = Path(__file__).resolve().parents[1]
CAT = json.loads((ROOT / "src/connors/catalog.json").read_text())
SPECS = {s["id"]: s for s in CAT["strategies"]}
md = nb.v4.new_markdown_cell
code = nb.v4.new_code_cell

BOOTSTRAP = """from pathlib import Path
import sys, subprocess, importlib.util, zipfile, io

try:
    import google.colab
    IN_COLAB = True
except ImportError:
    IN_COLAB = False

if IN_COLAB:
    PROJECT = Path("/content/larryconnors-trading")
    if not (PROJECT / "pyproject.toml").exists():
        from google.colab import files
        print("Upload the provided larryconnors-trading.zip project archive.")
        uploaded = files.upload()
        archives = [name for name in uploaded if name.endswith(".zip")]
        if len(archives) != 1:
            raise ValueError("Upload exactly one project ZIP")
        with zipfile.ZipFile(io.BytesIO(uploaded[archives[0]])) as archive:
            for name in archive.namelist():
                path = Path(name)
                if path.is_absolute() or ".." in path.parts or path.parts[0] != "larryconnors-trading":
                    raise ValueError("Unexpected archive layout")
            archive.extractall("/content")
        del uploaded
else:
    PROJECT = next((p for p in [Path.cwd(), *Path.cwd().parents]
                    if (p / "pyproject.toml").exists() and (p / "src/connors").exists()), None)
    if PROJECT is None:
        raise RuntimeError("Open this notebook from inside the extracted project folder")

assert (3, 11) <= sys.version_info[:2] < (3, 14), "Use Python 3.12 (tested)"
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q",
                       "-c", str(PROJECT / "constraints.txt"), "-e", str(PROJECT) + "[dev]"])
sys.path.insert(0, str(PROJECT / "src"))
print("Project ready:", PROJECT)
"""
IMPORTS = """# The official Alpaca SDK supplies historical data; vectorbt runs the portfolios.
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from connors.alpaca_sdk import read_notebook_secret
from connors.notebook import NotebookResearch, performance_matrix, display_performance_matrix
from connors.notebook_strategies import (
    PositionType, high_low_strategy, rsi_25_75_strategy, r3_strategy,
    percent_b_strategy, multiple_days_strategy, rsi_sma_strategy, tps_strategy,
    rsi_under_5_strategy, cumulative_rsi_strategy, double_seven_strategy,
    vix_rsi_strategy, trin_strategy, sp_short_strategy, ten_day_low_strategy,
    overnight_strategy, powerzones_strategy, crash_strategy, vol_panics_strategy,
    vxx_trend_strategy, new_highs_strategy, terror_gaps_strategy,
)

# Environment variables, Colab Secrets, or hidden interactive prompts.
# Do not replace these calls with literal secrets in saved cells.
API_KEY = read_notebook_secret("API_KEY")
API_SECRET = read_notebook_secret("API_SECRET")
client = StockHistoricalDataClient(API_KEY, API_SECRET)
del API_KEY, API_SECRET  # the SDK client retains its runtime credentials
"""
DEFAULTS = """# Change these defaults once, or override symbols/dates beside any strategy below.
SYMBOLS = ["SPY"]             # "SPY" or ["SPY", "QQQ", "IWM"]
start_date = "2022-01-03"    # first date of the backtest (warm-up is fetched automatically)
end_date = "2024-12-31"      # inclusive last date; choose completed historical sessions
FEED = "iex"                # "sip" if your Alpaca entitlement permits it
INITIAL_CAPITAL = 100_000    # independent capital PER ticker
EXECUTION_MODE = "source_close"  # "next_open" is a timing variant
ASSUME_BORROW_AVAILABLE = True   # explicit research assumption for short sections
BORROW_RATE = 0.0                # annual decimal; choose a nonzero estimate if appropriate

research = NotebookResearch(
    client, cache=PROJECT / ".cache/alpaca_sdk", output=PROJECT / "reports/notebooks",
    feed=FEED, adjustment="split", initial_capital=INITIAL_CAPITAL,
    execution_mode=EXECUTION_MODE, fees=0.0005, slippage=0.0005,
    assume_borrow_available=ASSUME_BORROW_AVAILABLE, borrow_rate=BORROW_RATE,
)
plot_all_stocks_pnl_charts = research.plot_all_stocks_pnl_charts
results = {}  # collected runs for the performance matrix at the end
"""

BOOKS = {
    "high_probability_etf_trading": (
        "High Probability ETF Trading",
        "hpe",
        [
            (
                "3-Day High/Low",
                "high_low_strategy",
                ["hpe.high_low.long", "hpe.high_low.short"],
            ),
            (
                "RSI 25 / RSI 75",
                "rsi_25_75_strategy",
                ["hpe.rsi4.long", "hpe.rsi4.short"],
            ),
            ("R3", "r3_strategy", ["hpe.r3.long", "hpe.r3.short"]),
            (
                "Bollinger %b",
                "percent_b_strategy",
                ["hpe.percent_b.long", "hpe.percent_b.short"],
            ),
            (
                "Multiple Days Down / Up",
                "multiple_days_strategy",
                ["hpe.multiple_days.long", "hpe.multiple_days.short"],
            ),
            (
                "RSI 10/6 / RSI 90/94 — RSI and SMA",
                "rsi_sma_strategy",
                ["hpe.rsi2_scale.long", "hpe.rsi2_scale.short"],
            ),
            (
                "TPS — Time, Price, Scale-in",
                "tps_strategy",
                ["hpe.tps.long", "hpe.tps.short"],
            ),
        ],
    ),
    "short_term_trading_strategies": (
        "Short Term Trading Strategies That Work",
        "short_term",
        [
            ("2-Period RSI Under 5", "rsi_under_5_strategy", ["short_term.rsi2"]),
            (
                "Cumulative RSI — Two-Day Sum",
                "cumulative_rsi_strategy",
                ["short_term.cumulative"],
            ),
            ("Double 7’s", "double_seven_strategy", ["short_term.double7"]),
            ("VIX RSI", "vix_rsi_strategy", ["short_term.vix"]),
            ("TRIN", "trin_strategy", ["short_term.trin"]),
            ("S&P Short", "sp_short_strategy", ["short_term.sp_short"]),
            (
                "Ten-Day Closing Low — Five-Day Hold",
                "ten_day_low_strategy",
                ["short_term.ten_day"],
            ),
            (
                "Overnight SPY Holding Test",
                "overnight_strategy",
                ["short_term.overnight"],
            ),
        ],
    ),
    "buy_the_fear_sell_the_greed": (
        "Buy the Fear, Sell the Greed",
        "buy_fear",
        [
            ("RSI PowerZones", "powerzones_strategy", ["buy_fear.powerzones"]),
            ("CRASH", "crash_strategy", ["buy_fear.crash"]),
            ("Vol Panics", "vol_panics_strategy", ["buy_fear.vol_panics"]),
            ("VXX Trend", "vxx_trend_strategy", ["buy_fear.vxx_trend"]),
            ("Trading New Highs", "new_highs_strategy", ["buy_fear.new_highs"]),
            (
                "TPS — Time, Price, Scale-in",
                "tps_strategy",
                ["hpe.tps.long", "hpe.tps.short"],
            ),
            (
                "Terror Gaps — specification blocked",
                "terror_gaps_strategy",
                ["buy_fear.terror_gaps"],
            ),
        ],
    ),
}


def run_cell(func, strategy_id, *, book, variant=None, key=None):
    spec = SPECS[strategy_id]
    direction = spec["direction"]
    kind = strategy_id.split(".")[1]
    steps = (
        [0.1, 0.2, 0.3, 0.4]
        if kind == "tps"
        else [0.5, 0.5] if kind in ["rsi2_scale", "powerzones"] else [1.0]
    )
    params = {}
    if variant:
        params = CAT["variants"][variant]["parameters"]
        if params.get("aggressive"):
            steps = [0.5, 0.5]
        if "stages" in params:
            steps = params["stages"]
    if book == "buy_fear" and kind == "tps" and not variant:
        variant = "tps_volume_" + direction
    symbols = '["VXX"]' if kind in ["vol_panics", "vxx_trend"] else "SYMBOLS"
    extra = ""
    if spec["status"] == "experimental":
        extra += (
            "    allow_experimental=True,  # explicit assumptions explained above\n"
        )
    if variant:
        extra += f"    variant={variant!r},\n"
    if kind == "r3":
        extra += '    parameters={"r3_interpretation": "first_declining_reading"},\n'
    if kind in ["vix", "trin"]:
        extra += "    auxiliary_csv=auxiliary_csv,\n"
    if kind == "overnight":
        extra += '    execution_mode="source_close",  # entry close, exit next open\n'
    key = key or variant or strategy_id
    return code(
        f"""# Inputs for this strategy — edit ticker(s), dates, direction or allocation here.
strategy_name = {spec['name']!r}
symbols = {symbols}  # accepts a single ticker string or a list
strategy_start_date = start_date
strategy_end_date = end_date

results[{key!r}] = plot_all_stocks_pnl_charts(
    symbols, strategy_start_date, strategy_end_date,
    strategy_name=strategy_name,
    position_type=PositionType.{direction.upper()},
    position_steps={steps!r},
    strategy_func={func},
{extra})
"""
    )


for filename, (title, book, sections) in BOOKS.items():
    cells = [
        md(
            f"""# {title}\n## Alpaca data → strategy signals → vectorbt trades → performance matrix

**How to use:** run Setup once, enter your credentials when prompted, set ticker(s) and dates, then run any strategy section. Each section has its own input cell. Use **Run All** to compare all documented strategies in this book. You do not need to edit YAML or package code.

**Local:** extract the project ZIP, open this notebook inside `notebooks/`, and use Python 3.12. **Colab:** upload this notebook, then upload the project ZIP when Setup asks. The same notebook works in both environments.

[Strategy reference]({CAT['sources'][book]}). Source-close results are idealized; next-open is an explicitly different timing assumption. This notebook defaults to real Alpaca data, never synthetic fallback.

### Contents
"""
            + "\n".join(f"{i}. {name}" for i, (name, _, __) in enumerate(sections, 1))
        ),
        md(
            """## 0. Setup — install the shared project

Run this cell once per fresh runtime. If NumPy/pandas were imported before installation and changed versions, restart the runtime and rerun Setup. Only Python 3.12 has been runtime-tested. The code lives in the shared package; these notebooks contain usage examples, not duplicated trading logic."""
        ),
        code(BOOTSTRAP),
        md(
            """### Alpaca credentials and imports

Set **API_KEY** and **API_SECRET** in your local environment or in Colab **Secrets** (enable notebook access). Otherwise, hidden input prompts appear. Keys stay in memory and are never printed or written into reports. No trading orders are submitted.

The package uses `StockHistoricalDataClient.get_stock_bars(StockBarsRequest(..., timeframe=TimeFrame.Day))`. SDK pagination retrieves all pages; the adapter caches bars across strategies and downloads warm-up history before your start date."""
        ),
        code(IMPORTS),
        md(
            """### Symbols, dates, costs and execution defaults

Your backtest starts on `start_date`; earlier bars only initialize indicators. Supply a string such as `"SPY"` or a list such as `["SPY", "QQQ"]`. Each ticker gets its own initial capital. The matrix compares independently funded runs, not a shared-cash portfolio.

`position_steps` expresses fractions of a planned full position, e.g. `[0.5, 0.5]` for two equal units or `[0.1, 0.2, 0.3, 0.4]` for TPS. Source equal-unit systems buy equal **shares**, so later dollar notionals can differ. `position_fraction=0.95` reserves room for costs; it can be changed per call. Unsupported extra stages are rejected, not invented.

Short sections below explicitly assume borrow availability; set the annual `BORROW_RATE` to your estimate. IEX is not consolidated SIP and volume-based screens can differ. Split-adjusted research prices exclude dividends; dollar-price screens on adjusted data are an approximation. A custom ticker is a user-selected universe experiment, not an automatic SPX/VIX proxy."""
        ),
        code(DEFAULTS),
        md(
            """### Reading the outputs

Each run returns a `NotebookBatch` with `.results[symbol].portfolio` (vectorbt), `.figures[symbol]`, and `.performance` (DataFrame). Charts show completed winning/losing positions, P&L, daily equity and drawdown. Scale-ins count as one position. Open final positions affect equity but not closed-trade win rate. Saved HTML charts and CSV ledgers are under `reports/notebooks/`.

The performance matrix uses daily-return Sharpe (252 sessions/year, zero risk-free), calendar-time CAGR for runs at least one year, net episode return divided by entered notional, and two-way turnover. Avoid treating vectorbt's internal three-phase event frequency as daily returns; the matrix uses actual daily closes."""
        ),
    ]
    for i, (name, func, ids) in enumerate(sections, 1):
        first = SPECS[ids[0]]
        rules = ""
        for strategy_id in ids:
            s = SPECS[strategy_id]
            rules += f"\n### {s['direction'].title()} rules\n\n- **Entry:** {s['entry_rules']}\n- **Additions:** {s['scale_in_rules']}\n- **Exit:** {s['exit_rules']}\n- **Default parameters:** `{json.dumps(s['parameters'])}`\n"
        notes = first.get("reason", "")
        if ids[0] == "hpe.percent_b.long":
            notes += " Bands use SMA(5), multiplier 1 and population standard deviation (ddof=0)."
        if ids[0] == "short_term.cumulative":
            notes += " This sums today’s RSI(2) and yesterday’s RSI(2), not RSI(4)."
        if ids[0] == "buy_fear.terror_gaps":
            notes += " The code cell below deliberately returns a blocked status. It must not create an entry price from a completed daily low."
        if book == "buy_fear" and ids[0] == "hpe.tps.long":
            notes += " This book’s calls use preceding-20-session average volume >=250000 as an explicit interpretation of its volume minimum."
        cells.append(
            md(
                f"## {i}. {name}\n\n**Source readiness:** {first['status']}. {notes}\n\n**Universe:** {first['universe']}\n"
                + rules
                + "\nAll “above/below” thresholds are strict; extrema ties qualify. Exits close the whole accumulated position."
            )
        )
        if ids[0] in ["short_term.vix", "short_term.trin"]:
            cells.append(
                md(
                    """### Supply the auxiliary index history

Alpaca stock bars do not supply this index. Set the CSV path below to actual VIX or NYSE TRIN data with a `date` index and `close` (plus `open` for VIX). Include the warm-up period and exact market sessions. No VXX-for-VIX substitution occurs. Leave `None` to see an explicit skipped row and continue running the book."""
                )
            )
            cells.append(
                code('auxiliary_csv = None  # e.g. str(PROJECT / "data/vix.csv")\n')
            )
        for strategy_id in ids:
            cells.append(run_cell(func, strategy_id, book=book))
        variants = [
            v
            for v, detail in CAT["variants"].items()
            if detail["strategy"] in ids
            and v not in ids
            and not v.startswith("tps_volume")
        ]
        if variants:
            cells.append(
                md(
                    """### Named variants — optional comparison

Each item below preserves its documented thresholds and scale-in rules. Set `RUN_VARIANTS = True` to run them on the same dates. Keep parameter exploration in training/validation data; do not choose the best variant on a final test period.

"""
                    + "\n".join(
                        f"- `{v}`: `{json.dumps(CAT['variants'][v]['parameters'])}`"
                        for v in variants
                    )
                )
            )
            calls = []
            for v in variants:
                sid = CAT["variants"][v]["strategy"]
                # Keep readable calls; wrap optional blocks without hiding inputs in package logic.
                source = run_cell(func, sid, book=book, variant=v).source
                calls.append(source)
            cells.append(
                code(
                    "RUN_VARIANTS = False\nif RUN_VARIANTS:\n"
                    + "\n".join("    " + line for line in "\n".join(calls).splitlines())
                    + "\n"
                )
            )
        if ids[0] == "buy_fear.powerzones":
            cells.append(
                md(
                    """### PowerZones 25/20 alternative

This is the same RSI(4) rule as aggressive HPE RSI25 long, with a second unit below20 and an exit above55. It remains distinct from RSI(2) systems."""
                )
            )
            cells.append(
                run_cell(
                    "rsi_25_75_strategy",
                    "hpe.rsi4.long",
                    book=book,
                    variant="powerzones25",
                )
            )
    cells.extend(
        [
            md(
                """## Book performance matrix

One row per strategy, direction and ticker. Skipped rows retain their reason. Rerunning a cell replaces that result in the in-memory comparison; every attempted configuration is still journaled on disk. This table is research output, not a recommendation."""
            ),
            code(
                '''matrix = performance_matrix(results)
display_performance_matrix(matrix)
output_file = PROJECT / "reports/notebooks" / "'''
                + filename
                + """_performance.csv"
output_file.parent.mkdir(parents=True, exist_ok=True)
matrix.to_csv(output_file, index=False)
print("Saved performance matrix:", output_file)
"""
            ),
            md(
                """## Inspect orders, trades and a vectorbt portfolio

Choose any successful strategy key and ticker from `results`. The returned objects remain available for additional vectorbt analysis. Fees include settled borrow charges; reported equity also deducts outstanding borrow liabilities."""
            ),
            code("""# Example (uncomment after a successful run):
# batch = next(batch for batch in results.values() if batch.results)
# ticker = next(iter(batch.results))
# portfolio = batch.results[ticker].portfolio
# display(batch.results[ticker].orders)
# display(portfolio.positions.records_readable)
# portfolio.positions.regroup(False)[ticker].closed.plot_pnl().show()
"""),
            md(
                """## Research limitations

Missing/duplicate sessions fail validation rather than being filled. VIX/TRIN need auxiliary data; incomplete source specifications remain blocked. Current ticker lists can have survivorship bias; VXX has historical product differences. No raw-price corporate-action ledger, live execution, historical locates, margin liquidation or automatic stop is added. Read `docs/methodology.md` and the source catalog for precise assumptions. Authenticated Alpaca and hosted Colab must be verified with your credentials; local notebook tests use mocked SDK responses, never fabricated market results."""
            ),
        ]
    )
    if book == "short_term":
        cells.append(
            md(
                """### Other mentions without executable rules

Cumulative RSI45 conflicts between RSI(3) over two days and RSI(2) over three days. Stock-specific Cumulative RSI omits necessary windows; VIX Stretches has conflicting exit equality; End of Month lacks a mandatory entry date. These are not runnable strategies and are listed as blocked in the catalog."""
            )
        )
    if book == "hpe":
        cells.append(
            md(
                """### Other mentions without executable rules

Promotional arbitrage/options systems, TPS235 and the four-or-five-of-six mention lack complete unambiguous specifications. They remain blocked; the seven core strategy families above are the executable coverage."""
            )
        )
    for j, c in enumerate(cells):
        c["id"] = f"{filename[:15]}-{j}"
    notebook = nb.v4.new_notebook(
        cells=cells,
        metadata={
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3.12"},
        },
    )
    nb.validate(notebook)
    nb.write(notebook, ROOT / "notebooks" / f"{filename}.ipynb")
    print(filename, len(cells), "cells")
