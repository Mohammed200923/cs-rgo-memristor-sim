"""Generate the results figures (Fig. 6-9) directly from the models."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from models.strukov import simulate_iv, compute_loop_area
from models.vteam import sweep_loading
from models.drift_diffusion import sweep_loading_physics
from models.synaptic import simulate_ltp_ltd, simulate_ppf, simulate_multilevel

OUT = os.path.join(os.path.dirname(__file__), "..", "figures")
os.makedirs(OUT, exist_ok=True)
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3de"
PHI_C = 22  # wt%, percolation threshold assumed in models/vteam.py and models/drift_diffusion.py

plt.rcParams.update({
    "font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.grid": True,
    "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False,
    "axes.spines.right": False, "legend.frameon": False, "lines.linewidth": 2,
    "savefig.dpi": 220, "savefig.bbox": "tight",
})


def panel(ax, letter, title):
    ax.set_title(f"({letter}) {title}", loc="left", fontsize=9, color=INK)


# Fig. 6 - Strukov model: I-V loops and loop area at 1, 5 and 20 Hz
freqs, colors = [1, 5, 20], [BLUE, ORANGE, AQUA]
fig, (a, b) = plt.subplots(1, 2, figsize=(7.2, 2.7))
areas = []
for f, c in zip(freqs, colors):
    t, v, i, x, R = simulate_iv(freq=f)
    areas.append(compute_loop_area(v, i))
    a.plot(v, i * 1e6, color=c, label=f"{f} Hz")
a.set_xlabel("Voltage (V)"); a.set_ylabel("Current (µA)"); a.legend(loc="upper left")
panel(a, "a", "I-V loops")
for k, (f, c, a_) in enumerate(zip(freqs, colors, areas)):
    b.plot(k, a_, "o", color=c, ms=8)
    b.annotate(f"{a_:.1e}", (k, a_), xytext=(10, -3), textcoords="offset points", color=INK, fontsize=8)
b.set_xticks(range(3), [f"{f} Hz" for f in freqs]); b.set_xlim(-0.5, 2.8)
b.set_yscale("log"); b.set_ylabel("Loop area (V·A)"); b.grid(axis="x", visible=False)
panel(b, "b", "Loop area vs drive frequency")
fig.savefig(os.path.join(OUT, "fig6_strukov.png")); plt.close(fig)

# Fig. 7 - VTEAM parameter map: ON/OFF, R_on and R_off vs rGO loading
vr = sweep_loading(np.arange(0, 25, 2))
phi = [r["phi"] for r in vr]
fig, (a, b) = plt.subplots(1, 2, figsize=(7.2, 2.7))
for ax in (a, b):
    ax.axvspan(PHI_C, 24.8, color=GRID, alpha=0.7, lw=0)
    ax.axvline(PHI_C, color=MUTED, lw=1, ls="--")
    ax.set_xlabel("rGO loading (wt%)"); ax.set_xlim(-0.8, 24.8)
a.plot(phi, [r["on_off"] for r in vr], color=BLUE, marker="o", ms=4)
pk = max(vr, key=lambda r: r["on_off"])
a.annotate(f"max {pk['on_off']:.0f} at {pk['phi']} wt%", (pk["phi"], pk["on_off"]),
           xytext=(-118, -4), textcoords="offset points", color=INK, fontsize=8)
a.set_yscale("log"); a.set_ylabel("ON/OFF ratio"); panel(a, "a", "ON/OFF ratio")
b.plot(phi, [r["R_off"] for r in vr], color=ORANGE, marker="o", ms=4, label="R_off")
b.plot(phi, [r["R_on"] for r in vr], color=BLUE, marker="o", ms=4, label="R_on")
b.set_yscale("log"); b.set_ylabel("Resistance (Ω)"); b.legend(loc="lower left", bbox_to_anchor=(0.36, 0.38))
panel(b, "b", "R_on and R_off")
fig.savefig(os.path.join(OUT, "fig7_vteam.png")); plt.close(fig)

# Fig. 8 - VTEAM parameter map vs drift-diffusion model
dr = sweep_loading_physics(np.arange(0, 25, 2))
fig, ax = plt.subplots(figsize=(7.2, 2.5))
ax.axvline(PHI_C, color=MUTED, lw=1, ls="--")
ax.plot(phi, [r["on_off"] for r in vr], color=BLUE, marker="o", ms=4, label="VTEAM parameter map")
ax.plot(phi, [r["on_off"] for r in dr], color=ORANGE, marker="s", ms=4, label="1-D drift-diffusion")
ax.set_yscale("log"); ax.set_xlabel("rGO loading (wt%)"); ax.set_ylabel("ON/OFF ratio")
ax.set_xlim(-0.8, 24.8); ax.legend(loc="upper left")
fig.savefig(os.path.join(OUT, "fig8_models.png")); plt.close(fig)

# Fig. 9 - Synaptic curves (phenomenological, parameters set in models/synaptic.py)
np.random.seed(0)  # multilevel read noise is random; fixed seed for a reproducible figure
fig, (a, b, c) = plt.subplots(1, 3, figsize=(7.2, 2.5))
p, G = simulate_ltp_ltd()
a.plot(p[:30], G[:30], color=BLUE, marker="o", ms=2.5, lw=1.5, label="Potentiation")
a.plot(p[30:], G[30:], color=ORANGE, marker="o", ms=2.5, lw=1.5, label="Depression")
a.set_xlabel("Pulse number"); a.set_ylabel("Conductance (µS)"); a.legend(fontsize=7)
panel(a, "a", "LTP / LTD")
dt, ppf = simulate_ppf()
b.plot(dt, ppf, color=BLUE); b.set_xscale("log")
b.set_xlabel("Pulse interval (ms)"); b.set_ylabel("PPF index (%)"); panel(b, "b", "Paired-pulse")
states = simulate_multilevel()
for k, s in enumerate(states):
    c.plot(np.arange(len(s)), s, color=BLUE, lw=1)
c.set_xlabel("Read number"); c.set_ylabel("Conductance (a.u.)"); panel(c, "c", "Six set levels")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig9_synaptic.png")); plt.close(fig)

print(f"Loop areas (V·A): " + ", ".join(f"{f} Hz {a_:.2e}" for f, a_ in zip(freqs, areas)))
print(f"VTEAM peak: {pk['phi']} wt%, ON/OFF {pk['on_off']:.0f}")
print(f"Drift-diffusion ON/OFF range: {min(r['on_off'] for r in dr):.2f}-{max(r['on_off'] for r in dr):.2f}")
print(f"Saved figures to {os.path.abspath(OUT)}")
