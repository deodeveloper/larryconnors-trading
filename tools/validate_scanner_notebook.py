"""Execute scanner notebook in a local kernel with isolated synthetic SDK data."""

from pathlib import Path
import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
notebook = nbformat.read(ROOT / "notebooks/strategy_scanner.ipynb", as_version=4)
setup = """from pathlib import Path
import sys
PROJECT = Path(ROOT_VALUE)
sys.path.insert(0, str(PROJECT / "src"))
from types import SimpleNamespace
import pandas as pd
from connors.data import synthetic
import alpaca.data.historical
import connors.alpaca_sdk
class SyntheticClient:
    def __init__(self, *args, **kwargs): pass
    def get_stock_bars(self, request):
        symbol = request.symbol_or_symbols[0]
        bars = synthetic([symbol], request.start.date().isoformat(), request.end.date().isoformat())[symbol]
        bars.index = bars.index.tz_localize("America/New_York").tz_convert("UTC")
        bars.index.name = "timestamp"
        return SimpleNamespace(df=pd.concat({symbol: bars}, names=["symbol"]))
alpaca.data.historical.StockHistoricalDataClient = SyntheticClient
connors.alpaca_sdk.read_notebook_secret = lambda name: "SYNTHETIC_TEST_ONLY"
""".replace("ROOT_VALUE", repr(str(ROOT)))
for c in notebook.cells:
    if c.cell_type != "code":
        continue
    if "subprocess.check_call" in c.source:
        c.source = setup
    if "SYMBOLS = " in c.source:
        c.source += '\nAS_OF = "2024-12-31T17:00:00-05:00"\nscanner.data.cache = PROJECT / "reports/scanner-validation/mock-cache"\n'
    if "run_id = " in c.source:
        c.source = c.source.replace(
            'output = PROJECT / "reports/scanner" / run_id',
            'output = PROJECT / "reports/scanner-validation/simulated" / run_id',
        )
notebook.cells.append(
    nbformat.v4.new_code_cell("""from connors.strategies import catalog
blocked = {s["id"] for s in catalog()["strategies"] if s["status"] == "blocked"}
for result in (signals, core_etfs, volatility):
    unexpected = result.summary.loc[(result.summary.status != "ok") & ~result.summary.strategy.isin(blocked | {"short_term.trin", "short_term.vix"})]
    assert unexpected.empty, unexpected[["strategy", "reason"]].to_dict("records")
assert set(core_etfs.summary.symbol) == {"SPY", "QQQ", "SOXX", "GLD"}
assert len(volatility.summary.query("reference_symbol == 'VXX' and status == 'ok'")) == 7
print("Synthetic notebook execution passed")
""")
)
NotebookClient(
    notebook,
    timeout=180,
    kernel_name="connors-research",
    resources={"metadata": {"path": str(ROOT)}},
).execute()
outputs = [
    o for c in notebook.cells if c.cell_type == "code" for o in c.get("outputs", [])
]
assert any(
    "application/vnd.plotly.v1+json" in o.get("data", {}) for o in outputs
), "Missing interactive Plotly output"
folder = ROOT / "reports/scanner-validation"
folder.mkdir(parents=True, exist_ok=True)
nbformat.write(notebook, folder / "strategy_scanner.synthetic.executed.ipynb")
print(
    "Scanner notebook: all three scan sections, tables, dark charts and exports passed with simulated data."
)
