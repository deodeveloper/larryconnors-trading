# Validation record

## Local Jupyter environment

Created a project-local `.venv` using CPython 3.12.14 on macOS arm64, with
JupyterLab 4.6.4 and Jupyter Notebook 7.6.3. The environment and kernel registration
are local artifacts, excluded from Git. `constraints-jupyter-py312.txt` captures
the resolved packages, and README.md documents recreation.

- All 47 project tests passed in this new environment.
- `pip check` found no broken requirements.
- The registered **Python (Connors Research)** kernel executed imports of the
  research package, vectorbt, pandas-ta-classic, Alpaca and Plotly successfully.
- `start_jupyter.sh --no-browser` started an authenticated localhost JupyterLab
  server; its kernelspec API returned the project kernel. The test shut down
  the server afterward. Browser interaction was not manually tested.
- No API keys or real market data were used in these checks.

## Current notebook release (0.2.0)

Tested locally with CPython 3.12.14 on macOS arm64. The three primary book notebooks
are `high_probability_etf_trading.ipynb`, `short_term_trading_strategies.ipynb`, and
`buy_the_fear_sell_the_greed.ipynb`.

- 47 tests passed. Full output is in `test-results.txt`.
- All three notebooks executed in actual local Jupyter kernels via nbclient with
  mocked Alpaca SDK responses. The installation cell was replaced by the already
  installed test environment; every default strategy cell, Plotly MIME output and
  styled performance matrix executed. These tests use synthetic data, not market
  evidence. Delivered notebooks have no saved outputs or credentials.
- Default notebook coverage: HPE 14 directional runs; Short Term 8 runs; Buy the
  Fear 9 runs (including both TPS directions and the PowerZones25 alternative).
  Only VIX/TRIN lacking auxiliary CSVs and Terror Gaps were expected to skip.
  Validation explicitly rejects any other skipped strategy.
- SDK pagination was exercised using the real StockHistoricalDataClient with a
  mocked multi-page HTTP response. Tests cover SDK requests, warm-up, cache reuse,
  transient retry, ticker normalization, single/list inputs, allocation overrides,
  blocked specifications, missing auxiliary inputs, zero trades, chart serialization,
  table rendering and absence of credentials from research logs.
- Existing indicator/execution tests continue to verify equality, Wilder/ConnorsRSI,
  cumulative sums, extrema, consecutive patterns, calendars, early closes, limit
  fills/expiry, next-open timing, scale-in restrictions, cash, full exits, short P&L,
  borrow accrual, independent capital and episode aggregation. Selected vectorbt
  results reconcile to a transparent cash/share ledger.
- `pip check` passed; wheel and source distributions built. Linux CPython3.12 SDK
  dependency wheels resolved under constraints.txt. Cross-platform pip resolution
  is not a hosted Colab runtime test; it can evaluate some host platform markers.
- Authenticated Alpaca calls and hosted Google Colab were **not** executed. The
  notebooks request API_KEY/API_SECRET at runtime and use real Alpaca data by
  default, with no synthetic fallback. Colab bootstrap/Secrets need verification
  in your runtime with your credentials.

To reproduce offline validation after installing development dependencies:

```bash
python -m pytest -q
python tools/validate_book_notebooks.py
```

The validator replaces data access only in executed test copies and writes them
under ignored `reports/notebook-validation/`. It isolates mocked bars from the
real-data cache. Optional named-variant loops default to disabled in delivered
notebooks; turn RUN_VARIANTS on deliberately for parameter research.

## Earlier baseline validation

The original framework completed 107 variant/execution-mode smoke runs and its
synthetic CLI/report workflows. The generic `research.ipynb` and `colab.ipynb`
remain as older demonstrations; the three book notebooks supersede them for
interactive strategy research. The standalone sample report was structurally
checked. Its browser preview was blocked by the in-app file-URL policy; no
screenshot-based report QA is claimed. Notebook rich outputs were exercised by
local kernels, not manually inspected in hosted Colab.

Known upstream warnings concern pandas deprecations and SDK websockets imports;
they do not cause test failures.
