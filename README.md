# Connors strategy research

A modular Python research framework built from the three Google Docs saved in
[docs/sources](docs/sources). Strategies are grouped under `src/connors/hpe`,
`short_term`, and `buy_fear`. No Google account is needed after checkout.

Uses **Alpaca historical bars**, **pandas-ta-classic**, **vectorbt**, and
**Plotly Express**. There is no live-order submission code.

## Setup (Python 3.12 recommended)

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

Set `APCA_API_KEY_ID` and `APCA_API_SECRET_KEY` in the runtime environment using your
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
