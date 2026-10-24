# Run a strategy by ticker and date

**Local launch:** from the project root run `./start_jupyter.sh` (or
`./start_jupyter.sh --classic` for Jupyter Notebook). Choose the
**Python (Connors Research)** kernel. See [local setup](../README.md#local-jupyter-setup)
to recreate the environment on another machine.

Open one of the three book notebooks in `notebooks/`. They are the same files for
local Jupyter and Colab. Each has source-linked Markdown rules and separate
strategy execution cells.

1. Run Setup. In Colab, upload the provided project ZIP when asked. Locally, open
   the notebook from inside the extracted project folder. Python3.12 is tested.
2. Supply `API_KEY` and `API_SECRET` in environment variables, Colab Secrets, or the
   hidden prompts. Do not save literal keys in a cell. The SDK is instantiated as
   `StockHistoricalDataClient(API_KEY, API_SECRET)`.
3. Set `SYMBOLS`, `start_date`, `end_date`, capital, costs and feed. The start date
   is the backtest start; earlier warm-up bars are downloaded automatically.
4. Run the section you want, or Run All. Change its local `symbols`,
   `strategy_start_date`, `strategy_end_date`, direction and allocation as needed.
5. Read the per-ticker charts and the book performance matrix at the end.

```python
results["rsi_spy"] = plot_all_stocks_pnl_charts(
    ["spy"], start_date, end_date,
    position_type=PositionType.LONG,
    position_steps=[0.5, 0.5],
    strategy_func=rsi_sma_strategy,
)

results["tps_etfs"] = plot_all_stocks_pnl_charts(
    ["SPY", "QQQ", "IWM"], "2022-01-03", "2024-12-31",
    position_type=PositionType.LONG,
    position_steps=[0.1, 0.2, 0.3, 0.4],
    strategy_func=tps_strategy,
)
```

`rsi_sma_strategy` is the HPE RSI2 10/6 long (90/94 short) system with the SMA5 exit,
not a generic ambiguous RSI crossover. All supported strategy callables are
imported in Setup; their book names are shown in the Markdown sections.

Each returned `NotebookBatch` contains:

- `performance`: DataFrame with strategy, symbol, dates, direction, status, total
  return, CAGR, drawdown, daily Sharpe, completed episodes, wins, losses, win rate,
  average episode return, profit factor, turnover and holding duration.
- `results["SPY"].portfolio`: the actual vectorbt portfolio.
- `results["SPY"].orders`: every attempted and filled order, including additions.
- `figures["SPY"]`: vectorbt position/trade and P&L plots plus daily equity/drawdown.

Each ticker gets independent initial capital. `position_fraction` defaults to95%
of equity for the planned full position. Source equal-unit systems use equal
shares; TPS/staged Vol Panics allocate incremental planned notionals. Changes to
source stage weights are labeled sizing experiments; extra undocumented stages
are rejected. Exits close the entire accumulated position.

`variant=` selects a named catalog variant. The optional loops in each relevant
section expose those exact names and numerical thresholds. `show=False` suppresses
inline display; `save=False` disables HTML/CSV exports (the research journal still
records the attempted configuration). `refresh=True` bypasses cached bars.

VIX/TRIN cells take `auxiliary_csv`; without the actual index history they return a
clear skipped row. Terror Gaps remains blocked. No index or ticker proxy is silently
substituted. Short research explicitly declares borrow availability and rate in
Setup. Source-close uses idealized same-close fills; next-open is a timing variant.
For full data, timing, corporate-action and metric conventions see methodology.md.


## History coverage and warm-up

The SDK requests a 600-session warm-up buffer. At least 300 complete sessions
before your backtest start are required, covering the implemented indicators,
including the nested 252-day high / 20-day window. If the feed begins later than
the requested buffer, an unavailable leading prefix is accepted only when that
minimum remains. No bars are filled and the backtest start is unchanged.
The exported data-quality record lists the actual first bar, available warm-up
count and every unavailable leading session. Internal gaps, missing backtest
sessions and insufficient warm-up still fail with date-specific diagnostics.

Alpaca [explains that IEX history begins in 2020 and SIP history in 2016](https://forum.alpaca.markets/t/cannot-get-historical-bar-data-before-2020/12415).
Feeds are never switched automatically. After updating the package, restart the
Jupyter kernel and rerun Setup so Python loads the updated loader. Use an end
date with completed daily bars; today's session may not yet be available.
