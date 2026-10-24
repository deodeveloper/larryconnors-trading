# Connors strategy research

A modular Python research framework built from the three Google Docs saved in
[docs/sources](docs/sources). Strategies are grouped under `src/connors/hpe`,
`short_term`, and `buy_fear`. No Google account is needed after checkout.

Uses **Alpaca historical bars**, **pandas-ta-classic**, **vectorbt**, and
**Plotly Express**. There is no live-order submission code.

## Current entry/exit scanner

Open [strategy_scanner.ipynb](notebooks/strategy_scanner.ipynb) in local Jupyter or
Colab. Enter one ticker or a list; it scans the three books for current entry/exit
conditions and recent entries without a later exit (latest session plus previous
three by default). Separate cells provide `scanner.scan_core_etfs()` for
SPY/QQQ/SOXX/GLD and `scanner.scan_volatility()` for VXX and VIX-conditioned SPY
signals. Actual VIX CSV data is required; VIX is never replaced with VXX.

Today's available partial bar is explicitly provisional. Missing current bars,
blocked strategies and missing index data produce visible reasons. This is a
hypothetical setup screen, not a broker holdings monitor. See the notebook's
Markdown sections for timing, limit fills, scheduled exits, universe experiments
and experimental-strategy assumptions. Tables and dark charts share package code.

## Start here: one notebook per book

Open any of these notebooks **locally or in Google Colab**. Run Setup, provide
`API_KEY` and `API_SECRET` through environment variables, Colab Secrets or hidden
prompts, and set your ticker(s) and dates. There is no YAML editing requirement.

| Notebook | Coverage |
| --- | --- |
| [High Probability ETF Trading](notebooks/high_probability_etf_trading.ipynb) | All 7 core families, long/short cells, named aggressive variants |
| [Short Term Trading Strategies](notebooks/short_term_trading_strategies.ipynb) | All 8 selected systems/tests, including auxiliary-data inputs |
| [Buy the Fear, Sell the Greed](notebooks/buy_the_fear_sell_the_greed.ipynb) | All 7 documented families; Terror Gaps explicitly blocked |

Every strategy section has Markdown rules and an input cell for strategy name,
ticker or ticker list, start date, end date, direction and position steps. For example,
after notebook Setup:

```python
results["my_rsi_run"] = plot_all_stocks_pnl_charts(
    ["SPY", "QQQ"], start_date, end_date,
    position_type=PositionType.LONG,
    position_steps=[0.5, 0.5],
    strategy_func=rsi_sma_strategy,
)
```

The notebook binding uses the official Alpaca SDK (`StockHistoricalDataClient`,
`StockBarsRequest`, `TimeFrame.Day`). It retrieves/cache-checks warm-up history,
then produces vectorbt completed-position trade and win/loss P&L charts, daily
equity/drawdown plots and a formatted performance matrix. Every ticker is funded
independently. Returned batches expose `.performance`, `.results[ticker].portfolio`,
and `.figures[ticker]` for further analysis. Results default to real Alpaca data;
there is no synthetic fallback in these book notebooks.

**Colab:** upload a book notebook, run Setup, and upload the supplied project ZIP
when prompted. **Local:** follow the Jupyter setup below. The same file works in either environment.
The older `research.ipynb` / `colab.ipynb` are generic synthetic demos; the three
book notebooks above are the primary workflow.

## Local Jupyter setup

The project-local `.venv` contains Python 3.12, the research package, JupyterLab,
Jupyter Notebook and a kernel named **Python (Connors Research)**. On this machine,
start it from Terminal with:

```bash
cd /Users/bijaydeo/development/codex/larryconnors-trading
./start_jupyter.sh
```

Your browser opens JupyterLab. Open `notebooks/` and choose one of the three book
notebooks above. Select **Python (Connors Research)** in the kernel picker (the
project's default Python 3 kernel also uses this environment). Run the setup cells,
enter your Alpaca keys at the hidden prompts, and edit the ticker list and dates.
Then run the desired strategy section to see its charts and performance matrix.
You do not need to activate the environment first. Keep Terminal open while using
Jupyter; press Ctrl+C there and confirm shutdown when finished.

For the traditional Jupyter Notebook interface:

```bash
./start_jupyter.sh --classic
```

### Recreate the environment on another machine

Install Python 3.12 first. From the project root:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -c constraints-jupyter-py312.txt -e '.[dev,notebook]'
.venv/bin/python -m ipykernel install --prefix "$PWD/.venv" --name connors-research --display-name "Python (Connors Research)"
./start_jupyter.sh
```

The environment is intentionally excluded from Git and the downloadable ZIP;
recreate it after extracting the project elsewhere. The local Jupyter constraints
were tested on macOS with Python 3.12. Colab uses its existing notebook frontend
and the installation cell in each book notebook, without this launcher.

## Command-line setup (Python 3.12 recommended)

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -c constraints.txt -e '.[dev]'
python -m pip check
python -m pytest -q
connors list
connors run configs/synthetic.yaml
```

Open `reports/synthetic/report.html`. This is deterministic synthetic data, not
historical performance. A checked-in demonstration is in
[examples/sample_report](examples/sample_report/report.html).

For hosts that disable editable `.pth` loading, use `PYTHONPATH=src python -m
connors.cli ...` and `PYTHONPATH=src python -m pytest`. A normal wheel install also
avoids editable-path loading. The Codex bundled Python required this workaround
inside its sandbox, but the same editable install worked outside it.

## Alpaca

Set `API_KEY` and `API_SECRET` (legacy CLI aliases `APCA_API_KEY_ID` and `APCA_API_SECRET_KEY` also work) in the runtime environment using your
secret manager. `.env.example` lists the names; `.env` files are not auto-executed
or committed. The code never prints credentials. Colab Secrets with the same
names are supported. Then:

```bash
connors fetch configs/alpaca_daily.yaml
connors run configs/alpaca_daily.yaml
connors variants configs/variants.yaml
connors report configs/synthetic.yaml --output reports/regenerated
```

`report` reproducibly reruns the saved configuration/data cache to regenerate all
exports. `fetch` supports Alpaca intraday timeframes as well as daily bars.
Set `aggregate_daily: true` with an intraday timeframe to reconstruct complete
regular sessions for daily book signals. An incomplete/misaligned interval grid
fails rather than inventing prices. Native Alpaca daily bars retain the provider's
bar convention; `regular_session` filtering applies to intraday data only.

For strict research partitions:

```bash
connors run configs/synthetic.yaml --split train
connors run configs/synthetic.yaml --split validation
connors run configs/synthetic.yaml --split test
```

Keep the final test configuration fixed. Multi-variant sweeps on a selected test
split are rejected. Every package run attempt is written to a JSONL research journal;
this is an audit trail, not a guarantee against manual data snooping.

## Catalog and readiness

Read [strategy_catalog.md](docs/strategy_catalog.md) and the complete machine
catalog [strategy_catalog.json](docs/strategy_catalog.json) before changing rules.
The catalog preserves source sections, numerical rules, timing, assumptions,
indicator definitions, source URLs, and named variants.

- HPE: 3-Day High/Low, RSI4 25/75, %b, Multiple Days Down/Up, RSI2 10/6 and 90/94,
  TPS; long and short directions and specified aggressive variants.
- Short Term: RSI2 under 5 market application, Cumulative RSI 35/50, Double7,
  VIX RSI, TRIN, S&P short, ten-day-low/five-day-hold, overnight SPY test.
- Buy the Fear: PowerZones 30/25; 25/20 deduplicated with aggressive HPE RSI4 long;
  CRASH, Vol Panics, VXX SMA/EMA trend, Trading New Highs. TPS references are
  deduplicated, with separate volume-filter variants.
- Experimental: R3 requires an explicit named first-reading interpretation;
  Cumulative RSI entry timing is not specified; CRASH/New Highs assume
  ConnorsRSI(3,2,100), rank ties, and historical-volatility conventions. Enable
  `allow_experimental: true` deliberately. Source omissions remain visible.
- Blocked: Terror Gaps has no unambiguous percentage reference price and needs
  post-open sequencing; Cumulative45 is conflicting; stock Cumulative RSI,
  VIX Stretches, end-of-month, promotional systems, and HPE TPS235 lack complete
  specifications. They cannot be run by adding an experimental flag.
- VIX/TRIN require supplied auxiliary CSVs. No automatic VXX-for-VIX or SPY-for-SPX
  proxy is allowed. SPY is a documented market application, not an SPX data alias.

## Notebooks and outputs

Use [notebooks/research.ipynb](notebooks/research.ipynb) locally and
[notebooks/colab.ipynb](notebooks/colab.ipynb) in Colab. Both import the package and
contain no duplicated signal or trading logic. The Colab notebook explains how to
upload the repository ZIP, install constraints, use Secrets, run and view reports.

Exports include configuration/source metadata and data quality, all attempted
orders, completed trading episodes, equity/drawdown/exposure, buy-and-hold,
per-symbol P&L, HTML charts, CSV, and JSON. An open final position is marked to
market and is excluded from closed-episode trade statistics.

## Execution and research limits

See [methodology](docs/methodology.md), [compatibility](docs/compatibility.md),
and [validation](docs/validation.md). Source-close is idealized completed-bar
same-close execution. Next-open is a timing variant. Equal-unit additions use
shares; TPS/Vol staged additions use fractions of a planned notional fixed when
an episode begins. Only filled orders advance stages. Exits have priority.

This is a research framework, not a reproduction of the books' historical tables.
Credentials and auxiliary market datasets were not provided; live Alpaca results
and hosted Colab execution have not been verified. All delivered performance
examples are simulated.
