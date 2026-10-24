"""Build the scanner notebook without rewriting the existing book notebooks."""

from pathlib import Path
import ast
import nbformat as nb

ROOT = Path(__file__).resolve().parents[1]
tree = ast.parse((ROOT / "tools/build_book_notebooks.py").read_text())
bootstrap = next(
    ast.literal_eval(node.value)
    for node in tree.body
    if isinstance(node, ast.Assign)
    and any(isinstance(t, ast.Name) and t.id == "BOOTSTRAP" for t in node.targets)
)
md = nb.v4.new_markdown_cell
code = nb.v4.new_code_cell
cells = [
    md("""# Current strategy scanner — all three books

Scan **one ticker or a list** for current entry and exit conditions. Find entries
from the latest session and the previous **three trading sessions** which have
not subsequently exited. Weekends and market holidays do not count as sessions.

Separate sections cover **your symbols**, **SPY / QQQ / SOXX / GLD**, and
**VXX / VIX-conditioned signals**. The same notebook works in local Jupyter and
Google Colab. It imports the shared rules; it does not duplicate trading logic.

This is a signal screen, not a backtest or an account-position monitor. “Active”
means a hypothetical eligible entry has no exit yet under source-close research
assumptions. No orders are submitted and no actual position, cash, borrow or
scale-in state is inferred."""),
    md("""## 1. Install / locate the project
Locally, launch `./start_jupyter.sh` from the project root and open this notebook.
In Colab, upload the current project ZIP when prompted. Use Python 3.12.
Restart the kernel after updating the package, then rerun these setup cells."""),
    code(bootstrap),
    md("""## 2. Alpaca credentials
Use environment variables or Colab Secrets named `API_KEY` and `API_SECRET`.
Otherwise hidden prompts will ask for them. Never save literal keys in a cell."""),
    code("""from alpaca.data.historical import StockHistoricalDataClient
from connors.alpaca_sdk import read_notebook_secret
from connors.scanner import StrategyScanner, show_scan
from IPython.display import display

client = StockHistoricalDataClient(
    read_notebook_secret("API_KEY"), read_notebook_secret("API_SECRET")
)
"""),
    md("""## 3. Inputs and timing
`LOOKBACK_SESSIONS = 4` means the latest session plus 1, 2 and 3 sessions ago.
With `AS_OF = None`, the scanner uses the current time in **America/New_York**.
On a holiday/weekend, it targets the previous trading day. On a trading day,
it targets today, including a **provisional** partial daily bar if available.
Before the open or when today's bar is unavailable, it reports unavailable data;
it never silently calls yesterday's signal today's signal. Provisional readings
can change. The calendar observes early closes; a 15-minute post-close buffer
also remains labeled provisional. These are provider daily bars, not reconstructed
regular-session intraday bars.

IEX and SIP differ. Choose a feed your account permits; the code never switches
feeds automatically. Recent SIP access can require a subscription. Timestamped
historical scans must use a completed session; completed daily bars cannot
reconstruct a historical intraday snapshot.

`ALLOW_EXPERIMENTAL = True` explicitly includes cataloged assumptions for R3,
Cumulative RSI, CRASH and Trading New Highs. Set it to False to exclude them.
Blocked strategies always appear with a reason. Named variants are separate rows,
so their counts overlap; matching variants are not independent confirmations.

Applying a book's rules to your chosen symbols is a recorded universe experiment,
not a claim that every ticker belonged to that book's original universe."""),
    code("""SYMBOLS = ["SPY", "QQQ"]  # or a single string: "AAPL"
LOOKBACK_SESSIONS = 4
AS_OF = None  # current time; or completed session: "2024-12-31T17:00:00-05:00"
FEED = "iex"  # choose "sip" explicitly if your entitlement supports it
ALLOW_EXPERIMENTAL = True
INCLUDE_VARIANTS = True
TRIN_CSV = None  # optional actual NYSE TRIN: date,close
VIX_CSV = None   # actual VIX daily data: date,open,close (separate section below)

scanner = StrategyScanner(
    client, feed=FEED, cache=PROJECT / ".cache/scanner",
    allow_experimental=ALLOW_EXPERIMENTAL,
    include_variants=INCLUDE_VARIANTS,
)
"""),
    md("""## 4. Scan your ticker(s)
All non-volatility strategies from the three books are considered. VIX and VXX
systems are excluded here. TRIN requires the optional actual index CSV; without
it that strategy is clearly unavailable. The screen includes both long and short
strategies where defined in the source catalog.

- **entry_now**: latest-bar entry conditions are true; a limit setup may still be pending.
- **exit_now**: latest-bar exit condition, or a scheduled exit for a hypothetical recent entry.
- **active_recent_entry**: an eligible recent entry has no subsequent exit, including today's.
- **entry_age_sessions**: 0 = latest session, 1 = previous session, up to 3 by default.
- **pending_limit**: a setup still awaits its next-session DAY limit fill.
- **status / reason**: distinguish unavailable or blocked rules from a genuine non-match.

A same-close entry/exit conflict is conservatively treated as exited. For
CRASH/New Highs, next-session OHLC must touch the limit; opening price improvement
is allowed, untouched DAY orders expire, and today's untouched limit remains
pending while the session is provisional. These are assumed fills, not verified
broker executions. Overnight entries exit at the next open; five-day holds expire
after five trading sessions. Scaling rules affect real positions but are not
additional initial-entry alerts in this screen."""),
    code("""signals = scanner.scan(
    SYMBOLS, lookback=LOOKBACK_SESSIONS, as_of=AS_OF, trin_csv=TRIN_CSV
)
show_scan(signals)
"""),
    md("""## 5. Dedicated SPY / QQQ / SOXX / GLD scan
The convenience method below always scans these four ETFs, using the same inputs
for lookback, timing and strategy readiness. Volatility systems stay separate."""),
    code("""core_etfs = scanner.scan_core_etfs(
    lookback=LOOKBACK_SESSIONS, as_of=AS_OF, trin_csv=TRIN_CSV
)
show_scan(core_etfs)
"""),
    md("""## 6. Separate VXX and VIX scan
**VXX:** Vol Panics (including named allocation/exit variants) and SMA/EMA trend
strategies use Alpaca VXX bars. VXX is not VIX; historical VXX product changes and
reverse splits matter, and split-adjusted prices are used.

**VIX:** the documented VIX RSI strategy uses actual VIX readings to signal a
**SPY trade**. Results identify `reference_symbol = VIX` and `symbol = SPY`.
VIX Stretches is blocked because its source rules are incomplete. No VXX-for-VIX
proxy is allowed. Alpaca stock bars are not assumed to supply the VIX index.

Set `VIX_CSV` to your actual VIX file, with `date,open,close` columns, one row per
session, at least 300 warm-up sessions before the scan window, and current data
through the target session. Additional columns are allowed. In Colab upload it
with the Files panel and set its `/content/...csv` path. Without it, VIX systems
are reported unavailable while VXX still runs. TRIN input follows the same date
coverage convention but only needs `date,close`. No missing values are filled.

The default four-session window is latest + previous three sessions, with the
same no-subsequent-exit condition used above."""),
    code("""volatility = scanner.scan_volatility(
    vix_csv=VIX_CSV, lookback=LOOKBACK_SESSIONS, as_of=AS_OF
)
show_scan(volatility)
"""),
    md("""## 7. Inspect the dates and export results
The event ledger retains setup dates, trading-session ages, hypothetical fill
prices, pending/expired limits and exit dates. Entries that exited are excluded
from the active table but retained here for inspection. Positions opened before
the lookback window are outside this screen; supply account positions separately
if you need an actual holdings monitor.

Exports contain source references, per-strategy readiness, scan configuration,
market-data quality and the timestamp. CSV/JSON exports go to ignored `reports/`.
Plots are interactive and use the shared dark theme."""),
    code("""display(signals.events)
display(volatility.events)
run_id = signals.metadata["as_of"].replace(":", "-")
output = PROJECT / "reports/scanner" / run_id
signals.save(output / "symbols")
core_etfs.save(output / "core_etfs")
volatility.save(output / "volatility")
print("Saved scan:", output)
"""),
    md("""## Sources and research limits
The source snapshots and full rule catalog are in `docs/sources/` and
`docs/strategy_catalog.md`. Every summary row includes its source references.
[Alpaca historical bars](https://docs.alpaca.markets/us/reference/stockbars) and
[feed/subscription details](https://docs.alpaca.markets/us/docs/market-data-faq)
explain the data endpoint and feed differences. No proxy datasets, stops or
hedges are silently added. Exits are rule conditions, not a recommendation to
close a position you may hold under a different strategy."""),
]
for i, c in enumerate(cells):
    c["id"] = f"scanner-{i}"
book = nb.v4.new_notebook(
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
nb.validate(book)
nb.write(book, ROOT / "notebooks/strategy_scanner.ipynb")
print("Created strategy_scanner.ipynb")
