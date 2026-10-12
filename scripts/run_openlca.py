"""Full LCIA of the six product systems via the openLCA IPC server.

Needs your local openLCA with the ecoinvent-based database open and
Tools > Developer tools > IPC server started (port 8080). Not runnable in CI:
the database is licensed and is NOT part of this repo.

    pip install olca-ipc olca-schema
    python scripts/run_openlca.py "IPCC 2013 GWP 100a"
"""
import sys, csv
from pathlib import Path
import olca_ipc as ipc
import olca_schema as o

METHOD = sys.argv[1] if len(sys.argv) > 1 else "IPCC 2013 GWP 100a"  # exact name as in your DB
SYSTEMS = ["RICE_1 - PK", "WHEAT_1 - PK", "Open Burning_Rice_1 - PK",
           "Open Burning_Wheat_1 - PK", "BIOCHAR-RICE-SEQ - PK", "BIOCHAR-WHEAT-SEQ - PK"]

client = ipc.Client(8080)
method = client.find(o.ImpactMethod, METHOD)
if method is None:
    sys.exit(f"Impact method not found: {METHOD}")

out = Path(__file__).resolve().parents[1] / "results" / "openlca_impacts.csv"
out.parent.mkdir(exist_ok=True)
with open(out, "w", newline="") as f:
    w = csv.writer(f); w.writerow(["product_system", "impact_category", "amount", "unit"])
    for name in SYSTEMS:
        ps = client.find(o.ProductSystem, name)
        if ps is None:
            print("not found:", name); continue
        setup = o.CalculationSetup(target=ps.to_ref(), impact_method=method.to_ref(), amount=1.0)
        result = client.calculate(setup)
        result.wait_until_ready()
        for i in result.get_total_impacts():
            w.writerow([name, i.impact_category.name, i.amount, i.impact_category.ref_unit])
        result.dispose()
print("wrote", out)
