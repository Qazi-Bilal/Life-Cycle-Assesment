"""Foreground climate-change model: crop production vs. residue management.

Only direct (foreground) emissions are characterised here. Background
processes (fertiliser, diesel supply, ...) need ecoinvent; see
scripts/run_openlca.py for the full calculation.
"""
from pathlib import Path
import yaml

DATA = Path(__file__).resolve().parents[2] / "data"

# kg CO2e per kg, IPCC AR6 GWP100. Biogenic ("non-fossil") CO2 is neutral;
# the soil-storage credit is entered as a negative "from soil or biomass stock" flow.
GWP100 = {
    "Carbon dioxide, fossil": 1.0,
    "Carbon dioxide, non-fossil": 0.0,
    "Carbon dioxide, from soil or biomass stock": 1.0,
    "Methane, non-fossil": 27.0,
    "Nitrous oxide (direct, N2O)": 273.0,
}


def load_inventories(path=None):
    with open(path or DATA / "foreground_inventories.yaml") as f:
        return yaml.safe_load(f)


def gwp(process):
    """Return {flow: kg CO2e} for one process's output flows with a GWP factor."""
    return {
        flow: amount * GWP100[flow]
        for flow, (amount, _unit) in process["outputs"].items()
        if flow in GWP100
    }


def total(process):
    return sum(gwp(process).values())


def scenarios(crop):
    """Scenario -> list of process keys, for crop 'rice' or 'wheat'."""
    return {
        "Crop + open burning of straw": [f"{crop}_crop", f"{crop}_open_burning"],
        "Crop + biochar from straw": [f"{crop}_crop", f"{crop}_pyrolysis", f"{crop}_biochar_soil"],
    }


def run_all(inv=None):
    inv = inv or load_inventories()
    rows = []
    for crop in ("rice", "wheat"):
        for name, keys in scenarios(crop).items():
            for k in keys:
                for flow, v in gwp(inv[k]).items():
                    rows.append(dict(crop=crop, scenario=name, process=k, flow=flow, kg_co2e=v))
    return rows
