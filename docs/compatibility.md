# Compatibility and official documentation

Checked 2026-10-23 (America/Los_Angeles). Actual clean local runtime: CPython3.12.14,
macOS arm64. The host's default Python3.9 is too old and was not used for this stack.

Core pinned versions: pandas-ta-classic0.8.32, vectorbt1.2.0, Plotly7.1.0,
pandas3.1.0, NumPy2.5.4, numba0.68.0, exchange-calendars4.13.2.
`constraints.txt` pins all resolved transitive packages; the macOS freeze is retained
separately. Install project and dev extras under those constraints. This is a
version lock, not a hash-verified artifact lock. Runtime support is restricted to
Python3.11–3.13; only3.12 was executed here.

Official references checked before choosing the installed versions:

- [pandas-ta-classic installation](https://xgboosted.github.io/pandas-ta-classic/installation.html)
- [pandas-ta-classic source and releases](https://github.com/xgboosted/pandas-ta-classic)
- [vectorbt Portfolio API](https://vectorbt.dev/api/portfolio/base/)
- [Alpaca historical stock bars](https://docs.alpaca.markets/us/reference/stockbars)
- [Alpaca Python request schema](https://alpaca.markets/sdks/python/api_reference/data/stock/requests.html)
- [Plotly Express](https://plotly.com/python-api-reference/generated/plotly.express.line)

The Alpaca adapter uses its documented REST API directly with requests, allowing
pagination/retries/cache to be tested explicitly; no substitute market-data provider.
Installed pandas-ta-classic RSI/RMA source was inspected and arithmetic seed checked
against hand calculations. SMA, EMA and Bollinger calculations use that library;
ConnorsRSI, rank, cumulative sums and HV are explicit compositions/custom definitions.
Portfolio accounting uses vectorbt.from_order_func, not a replacement backtester.

Colab: the notebook is intended for a Python3.12 runtime. Linux x86_64 wheel
resolution is checked with pip's platform/ABI flags; that checks package artifacts,
not runtime behavior in hosted Colab. Direct hosted Colab execution and Secrets
integration could not be tested here. Restart the Colab runtime after installing
if older NumPy/pandas were already imported. Do not force-install incompatible
packages into an older Python runtime; choose a matching runtime or use local3.12.
