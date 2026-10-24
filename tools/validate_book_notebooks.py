"""Execute every book's default cells in a kernel using a mocked Alpaca SDK.

No market-data credentials or network calls. Executed copies stay in reports/.
The installation cell is replaced because dependencies are installed by test setup.
"""

from pathlib import Path
import json
import sys
import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP = f"""
from pathlib import Path
import sys, os
PROJECT = Path({str(ROOT)!r})
sys.path.insert(0, str(PROJECT / "src"))
os.environ["API_KEY"] = "FAKE_NOTEBOOK_TEST_KEY"
os.environ["API_SECRET"] = "FAKE_NOTEBOOK_TEST_SECRET"
from types import SimpleNamespace
import pandas as pd
from connors.data import synthetic
from alpaca.data.historical import StockHistoricalDataClient
import plotly.io as pio
pio.renderers.default = "plotly_mimetype"
def mock_get_stock_bars(self, request):
    symbol = request.symbol_or_symbols[0]
    end = (pd.Timestamp(request.end).tz_localize("UTC").tz_convert("America/New_York").normalize() - pd.Timedelta(days=1)).date().isoformat()
    bars = synthetic([symbol], request.start.date().isoformat(), end)[symbol]
    bars.index = bars.index.tz_localize("America/New_York").tz_convert("UTC")
    bars.index.name = "timestamp"
    return SimpleNamespace(df=pd.concat({{symbol: bars}}, names=["symbol"]))
StockHistoricalDataClient.get_stock_bars = mock_get_stock_bars
"""


def main():
    output = ROOT / "reports/notebook-validation"
    output.mkdir(parents=True, exist_ok=True)
    summary = {}
    for name in [
        "high_probability_etf_trading",
        "short_term_trading_strategies",
        "buy_the_fear_sell_the_greed",
    ]:
        notebook = nbformat.read(ROOT / "notebooks" / f"{name}.ipynb", as_version=4)
        for cell in notebook.cells:
            if cell.cell_type != "code":
                continue
            if "subprocess.check_call" in cell.source:
                cell.source = BOOTSTRAP
            elif "research = NotebookResearch(" in cell.source:
                # Keep mocked bars out of the real Alpaca cache and real run exports.
                cell.source = cell.source.replace(
                    'PROJECT / ".cache/alpaca_sdk"', repr(str(output / name / "cache"))
                )
                cell.source = cell.source.replace(
                    'PROJECT / "reports/notebooks"', repr(str(output / name / "runs"))
                )
                cell.source += "\nfrom functools import partial\nplot_all_stocks_pnl_charts = partial(plot_all_stocks_pnl_charts, save=False)\n"
            else:
                cell.source = cell.source.replace(
                    'PROJECT / "reports/notebooks"',
                    f"Path({str(output / name / 'runs')!r})",
                )
        notebook.cells.append(nbformat.v4.new_code_cell("""
assert not matrix.empty
assert (matrix.status == "ok").any()
allowed_skips = {"short_term.vix", "short_term.trin", "buy_fear.terror_gaps"}
assert set(matrix.loc[matrix.status != "ok", "variant"]).issubset(allowed_skips)
for batch in results.values():
    for figures in batch.figures.values():
        assert all(figure.to_json() for figure in figures.values())
print(matrix[["strategy", "symbol", "direction", "status"]].to_string(index=False))
"""))
        client = NotebookClient(
            notebook,
            timeout=240,
            kernel_name="python3",
            resources={"metadata": {"path": str(ROOT)}},
        )
        client.execute()
        nbformat.write(notebook, output / f"{name}.executed.ipynb")
        summary[name] = {
            "cells": len(notebook.cells),
            "status": "passed",
            "data": "mocked SDK; synthetic",
        }
        print(name, "passed", flush=True)
    (output / "summary.json").write_text(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
