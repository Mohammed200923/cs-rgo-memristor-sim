"""Run all simulations and generate CSV data."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from models.strukov import simulate_iv, compute_lobe_area
from models.vteam import sweep_loading, FINE_GRID
from models.drift_diffusion import sweep_loading_physics
from models.synaptic import simulate_ltp_ltd, simulate_ppf, simulate_multilevel

print("="*60)
print("CS-rGO Memristor Simulation Suite")
print("="*60)

print("\n[1/4] Strukov validation...")
areas = []
for f in [1, 5, 20]:
    t, v, i, x, R = simulate_iv(freq=f)
    areas.append(compute_lobe_area(t, v, i, f))
    print(f"  f={f} Hz: single-lobe area={areas[-1]:.2e} V*A")
print(f"  Area ratio 1 Hz / 20 Hz: {areas[0]/areas[-1]:.1f}x")
print("  Decreases monotonically with frequency:", all(a > b for a, b in zip(areas, areas[1:])))

print("\n[2/4] Empirical parameter map...")
phi = np.arange(0, 25, 2)
vr = sweep_loading(phi)
pk = max(vr, key=lambda r: r["on_off"])
fine = sweep_loading(FINE_GRID)
fmax = max(fine, key=lambda r: r["on_off"])
at = {round(r["phi"], 1): r["on_off"] for r in fine}
print(f"  2 wt% grid: highest point {pk['on_off']:.0f} at {pk['phi']} wt%")
print(f"  0.1 wt% grid: {at[20.0]:.0f} at 20 wt%, {at[21.8]:.0f} at 21.8 wt%, max {fmax['on_off']:.0f} at {fmax['phi']} wt%")
print("  No interior peak: the ratio rises until the assumed threshold (22 wt%)")

print("\n[3/4] Drift-diffusion cross-check...")
dr = sweep_loading_physics(phi)
dd = [r["on_off"] for r in dr]
if max(dd) - min(dd) < 1e-6:
    print(f"  ON/OFF = {dd[0]:.2f} at every loading: no peak, no cross-check")
else:
    pk2 = max(dr, key=lambda r: r["on_off"])
    print(f"  Peak: phi={pk2['phi']} wt%")
    print(f"  Agreement with map (within 4 wt%): {'YES' if abs(pk['phi']-pk2['phi'])<=4 else 'NO'}")

print("\n[4/4] Synaptic behavior...")
p, G = simulate_ltp_ltd()
dt, ppf = simulate_ppf()
states = simulate_multilevel()
print(f"  LTP/LTD: [{G.min():.2f}, {G.max():.2f}] uS")
print(f"  PPF peak: {ppf.max():.1f}%")
print(f"  States: {len(states)}")

out = os.path.join(os.path.dirname(__file__), "..", "data", "simulation_results.csv")
with open(out, "w") as f:
    f.write("rGO_wt%,ON_OFF_VTEAM,ON_OFF_DriftDiffusion\n")
    for v, d in zip(vr, dr):
        f.write(f"{v['phi']},{v['on_off']:.1f},{d['on_off']:.1f}\n")
print(f"\nSaved: {out}")
print("\n" + "="*60)
after = [r for r in vr if r["phi"] > pk["phi"]]
drop = next((r["phi"] for r in after if r["on_off"] < 0.1 * pk["on_off"]), None)
print(f"MAP: ON/OFF in the 10^3 range just below the threshold (max {fmax['on_off']:.0f} at {fmax['phi']} wt%) | COLLAPSE AT: {drop} wt%")
print("The maximum sits at the assumed percolation threshold (22 wt%) in models/vteam.py")
print("="*60)
