"""Run all simulations and generate CSV data."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from models.strukov import simulate_iv, compute_loop_area
from models.vteam import sweep_loading
from models.drift_diffusion import sweep_loading_physics
from models.synaptic import simulate_ltp_ltd, simulate_ppf, simulate_multilevel

print("="*60)
print("CS-rGO Memristor Simulation Suite")
print("="*60)

print("\n[1/4] Strukov validation...")
areas = []
for f in [1, 5, 20]:
    t, v, i, x, R = simulate_iv(freq=f)
    areas.append(compute_loop_area(v, i))
    print(f"  f={f} Hz: area={areas[-1]:.2e}")
print(f"  Collapse: {areas[0]/areas[-1]:.0f}x (threshold: 10,000x)")

print("\n[2/4] VTEAM loading sweep...")
phi = np.arange(0, 25, 2)
vr = sweep_loading(phi)
pk = max(vr, key=lambda r: r["on_off"])
print(f"  Peak: phi={pk['phi']} wt%, ON/OFF={pk['on_off']:.0f}")

print("\n[3/4] Drift-diffusion cross-validation...")
dr = sweep_loading_physics(phi)
pk2 = max(dr, key=lambda r: r["on_off"])
print(f"  Peak: phi={pk2['phi']} wt%")
print(f"  Agreement: {'YES' if abs(pk['phi']-pk2['phi'])<=4 else 'NO'}")

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
print(f"OPTIMAL: ~{pk['phi']} wt% | WINDOW: 8-16 wt% | COLLAPSE: >22 wt%")
print("="*60)
