"""Run the foreground GWP100 comparison and write results/ (CSV + chart)."""
import sys, csv
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from biochar_lca import load_inventories, run_all

rows = run_all(load_inventories())
out = ROOT / "results"; out.mkdir(exist_ok=True)
with open(out / "gwp_by_flow.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)

tot = defaultdict(float); by_proc = defaultdict(float)
for r in rows:
    tot[(r["crop"], r["scenario"])] += r["kg_co2e"]
    by_proc[(r["crop"], r["scenario"], r["process"])] += r["kg_co2e"]
with open(out / "gwp_by_scenario.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["crop", "scenario", "net_kg_co2e_per_ha"])
    for (c, s), v in tot.items(): w.writerow([c, s, round(v, 1)])
    for (c, s), v in tot.items(): print(f"{c:6} {s:32} {v:10.0f} kg CO2e/ha")

# chart: net GWP per scenario, per crop
fig, ax = plt.subplots(figsize=(7, 3.6))
cols = {"Crop + open burning of straw": "#eb6834", "Crop + biochar from straw": "#2a78d6"}
x = 0
for crop in ("rice", "wheat"):
    for s, c in cols.items():
        ax.bar(x, tot[(crop, s)], color=c, width=0.7, label=s if crop == "rice" else None)
        ax.annotate(f"{tot[(crop, s)]:,.0f}", (x, tot[(crop, s)]), ha="center", va="bottom" if tot[(crop, s)] >= 0 else "top", fontsize=9, xytext=(0, 3 if tot[(crop, s)] >= 0 else -3), textcoords="offset points")
        x += 1
    x += 0.6
ax.set_xticks([0.5, 3.1]); ax.set_xticklabels(["Rice", "Wheat"])
ax.margins(y=0.15)
ax.axhline(0, color="#52514e", lw=0.8)
ax.set_ylabel("kg CO$_2$e per ha (foreground only)")
ax.set_title("Climate change (GWP100): open burning vs biochar", loc="left", fontsize=11)
for sp in ("top", "right"): ax.spines[sp].set_visible(False)
ax.legend(frameon=False, fontsize=9)
fig.tight_layout(); fig.savefig(out / "gwp_comparison.png", dpi=160)
