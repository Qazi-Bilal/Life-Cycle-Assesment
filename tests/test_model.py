import sys; from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from biochar_lca import load_inventories, gwp

def test_biochar_credit_negative():
    inv = load_inventories()
    assert sum(gwp(inv["rice_biochar_soil"]).values()) < 0

def test_open_burning_methane_only():
    inv = load_inventories()
    g = gwp(inv["rice_open_burning"])
    assert abs(g["Methane, non-fossil"] - 23.99181954 * 27) < 1e-6
    assert g["Carbon dioxide, non-fossil"] == 0
