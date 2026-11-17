"""Check that the saved data and the reported headline numbers match the models.

Run from the project folder:  python tests/test_results.py
"""
import sys, os, csv
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from models.strukov import simulate_iv, compute_lobe_area, compute_loop_area
from models.vteam import sweep_loading, FINE_GRID
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
    assert pk["phi"] == 20 and round(pk["on_off"]) == 1489          # highest point on the 2 wt% grid
    assert [r["on_off"] for r in vr if r["phi"] == 22][0] < 3       # collapse at 22 wt%
    fine = sweep_loading(FINE_GRID)
    ratios = [r["on_off"] for r in fine]
    assert all(b >= a for a, b in zip(ratios, ratios[1:]))          # no interior peak below phi_c
    at = {round(r["phi"], 1): r["on_off"] for r in fine}
    assert round(at[21.8]) == 3554 and 1e3 <= max(ratios) < 1e4     # 10^3 range just below threshold
    dd = [r["on_off"] for r in sweep_loading_physics(PHI)]
    assert max(dd) - min(dd) < 1e-6                                 # drift-diffusion is flat
    areas = []
    for f in (1, 5, 20):
        t, v, i, _, _ = simulate_iv(freq=f)
        areas.append(compute_lobe_area(t, v, i, f))
    assert areas[0] > areas[1] > areas[2]                           # single lobe falls with frequency
    for got, want in zip(areas, (4.2e-5, 3.1e-6, 6.9e-7)):
        assert abs(got / want - 1) < 0.02                           # values on the poster


def test_lobe_area_converges_and_whole_trace_cancels():
    for f in (1, 20):
        coarse = simulate_iv(freq=f)
        fine = simulate_iv(freq=f, dt=1.0 / (f * 40000))
        a1 = compute_lobe_area(coarse[0], coarse[1], coarse[2], f)
        a2 = compute_lobe_area(fine[0], fine[1], fine[2], f)
        assert abs(a1 / a2 - 1) < 0.01                              # stable under a 10x finer step
        assert compute_loop_area(fine[1], fine[2]) < 1e-3 * a2      # two lobes cancel: old metric was noise
    assert round(simulate_ppf()[1].max()) == 169                    # set by A = 70
    assert len(simulate_multilevel()) == 6                          # set by n_states = 6


if __name__ == "__main__":
    test_csv_matches_models()
    test_reported_headline_numbers()
    test_lobe_area_converges_and_whole_trace_cancels()
    print("All checks passed: data and reported numbers match the models.")
