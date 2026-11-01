"""Check that the saved data and the reported headline numbers match the models.

Run from the project folder:  python tests/test_results.py
"""
import sys, os, csv
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from models.strukov import simulate_iv, compute_loop_area
from models.vteam import sweep_loading
from models.drift_diffusion import sweep_loading_physics
from models.synaptic import simulate_ppf, simulate_multilevel

HERE = os.path.dirname(__file__)
PHI = np.arange(0, 25, 2)


def test_csv_matches_models():
    vr, dr = sweep_loading(PHI), sweep_loading_physics(PHI)
    with open(os.path.join(HERE, "..", "data", "simulation_results.csv")) as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == len(PHI)
    for row, v, d in zip(rows, vr, dr):
        assert int(row["rGO_wt%"]) == v["phi"]
        assert abs(float(row["ON_OFF_VTEAM"]) - v["on_off"]) < 0.1
        assert abs(float(row["ON_OFF_DriftDiffusion"]) - d["on_off"]) < 0.1


def test_reported_headline_numbers():
    vr = sweep_loading(PHI)
    pk = max(vr, key=lambda r: r["on_off"])
    assert pk["phi"] == 20 and round(pk["on_off"]) == 1489          # map peak
    assert [r["on_off"] for r in vr if r["phi"] == 22][0] < 3       # collapse at 22 wt%
    dd = [r["on_off"] for r in sweep_loading_physics(PHI)]
    assert max(dd) - min(dd) < 1e-6                                 # drift-diffusion is flat
    areas = [compute_loop_area(*simulate_iv(freq=f)[1:3]) for f in (1, 5, 20)]
    assert areas[0] > areas[1] and areas[2] > areas[1]              # not monotonic
    assert round(simulate_ppf()[1].max()) == 169                    # set by A = 70
    assert len(simulate_multilevel()) == 6                          # set by n_states = 6


if __name__ == "__main__":
    test_csv_matches_models()
    test_reported_headline_numbers()
    print("All checks passed: data and reported numbers match the models.")
