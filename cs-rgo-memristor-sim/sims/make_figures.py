"""Generate the results figures (Fig. 6-9) directly from the models."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from models.strukov import simulate_iv, compute_lobe_area
from models.vteam import sweep_loading, FINE_GRID
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


# Figs. 6-8 use larger type: they are printed on the 36 x 48 in SAIF poster.
POSTER = {"font.size": 17, "axes.titlesize": 17, "axes.labelsize": 17, "xtick.labelsize": 15,
          "ytick.labelsize": 15, "legend.fontsize": 15, "axes.grid": False}
RED, GREY = "#b2483a", "#6b7b78"

# Fig. 6 - Strukov model: I-V loops and single-lobe area at 1, 5 and 20 Hz
freqs, colors = [1, 5, 20], [BLUE, ORANGE, AQUA]
areas = []
with plt.rc_context(POSTER):
    fig, (a, b) = plt.subplots(1, 2, figsize=(10, 4.6), gridspec_kw={"width_ratios": [1.15, 1]})
    for f, c in zip(freqs, colors):
        t, v, i, x, R = simulate_iv(freq=f)
        areas.append(compute_lobe_area(t, v, i, f))
        m = t >= 1.0 / f  # second cycle (settled loop)
        a.plot(v[m], i[m] * 1e6, color=c, lw=2.4, label=f"{f} Hz")
    a.axhline(0, color="#999", lw=.8); a.axvline(0, color="#999", lw=.8)
    a.set_xlabel("Voltage (V)"); a.set_ylabel("Current (µA)"); a.legend(loc="upper left")
    a.set_title("(a) I-V loops", loc="left")
    fs, ar = np.array(freqs), np.array(areas)
    b.loglog(fs, ar, "o-", color=RED, lw=2.4, ms=10)
    for f, y in zip(fs, ar):
        b.annotate(f"{y:.1e}", (f, y), textcoords="offset points", xytext=(10, 6), fontsize=15)
    b.set_xticks(fs); b.set_xticklabels([f"{f} Hz" for f in freqs]); b.minorticks_off()
    b.set_xlim(0.7, 40); b.set_ylim(ar.min() / 2, ar.max() * 3)
    b.set_ylabel("Single-lobe area (V·A)"); b.set_title("(b) Loop area vs frequency", loc="left")
    b.grid(True, which="major", alpha=.3)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig6_strukov.png")); plt.close(fig)

# Fig. 7 - Empirical parameter map on a 0.1 wt% grid (2 wt% points shown for comparison)
fine = sweep_loading(FINE_GRID)
coarse = [r for r in sweep_loading(np.arange(0, 21, 2))]
phi_f = [r["phi"] for r in fine]
with plt.rc_context(POSTER):
    fig, (a, b) = plt.subplots(1, 2, figsize=(10, 4.6))
    for ax in (a, b):
        ax.axvspan(PHI_C, 25, color="#e9e6dc", lw=0); ax.axvline(PHI_C, color=GREY, ls="--", lw=1.6)
        ax.set_xlim(0, 25); ax.set_xlabel("rGO loading (wt%)")
    a.semilogy(phi_f, [r["on_off"] for r in fine], color=BLUE, lw=3, label="0.1 wt% grid")
    a.semilogy([r["phi"] for r in coarse], [r["on_off"] for r in coarse], "o", color=BLUE,
               mfc="white", ms=8, mew=2, label="2 wt% grid")
    a.set_ylabel("ON/OFF ratio"); a.set_title("(a) ON/OFF ratio", loc="left"); a.set_ylim(3, 2e4)
    a.text(23.5, 8e3, "short", fontsize=15, color=GREY, ha="center", rotation=90, va="top")
    a.annotate("10³ range", (21.3, 2.8e3), xytext=(9.0, 6e3), fontsize=17, color=RED, fontweight="bold",
               arrowprops=dict(arrowstyle="->", color=RED, lw=2))
    a.legend(loc="lower right", bbox_to_anchor=(0.86, 0.0))
    b.semilogy(phi_f, [r["R_off"] for r in fine], color=ORANGE, lw=3, label="R_off")
    b.semilogy(phi_f, [r["R_on"] for r in fine], color=BLUE, lw=3, label="R_on")
    b.set_ylabel("Resistance (Ω)"); b.set_title("(b) R_on and R_off", loc="left"); b.legend(loc="center left")
    for ax in (a, b):
        ax.grid(True, which="major", alpha=.3)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig7_vteam.png")); plt.close(fig)

# Fig. 8 - Parameter map vs drift-diffusion model
phi = np.arange(0, 25, 2)
dr = sweep_loading_physics(phi)
with plt.rc_context(POSTER):
    fig, ax = plt.subplots(figsize=(10, 4.4))
    ax.axvspan(PHI_C, 25, color="#e9e6dc", lw=0); ax.axvline(PHI_C, color=GREY, ls="--", lw=1.6)
    ax.semilogy(phi_f, [r["on_off"] for r in fine], color=BLUE, lw=3, label="Empirical parameter map")
    ax.semilogy(phi, [r["on_off"] for r in dr], "s-", color=ORANGE, lw=2.4, ms=8,
                label="1-D drift-diffusion (ON/OFF = 1)")
    ax.set_xlim(0, 25); ax.set_ylim(0.5, 2e4)
    ax.set_xlabel("rGO loading (wt%)"); ax.set_ylabel("ON/OFF ratio")
    ax.legend(loc="upper left"); ax.grid(True, which="major", alpha=.3)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig8_models.png")); plt.close(fig)

# Fig. 9 - Synaptic target curves (phenomenological; parameters chosen in models/synaptic.py)
np.random.seed(0)  # multilevel read noise is random; fixed seed for a reproducible figure
with plt.rc_context(POSTER):
    fig, (a, b, c) = plt.subplots(1, 3, figsize=(10, 4.2))
    p, G = simulate_ltp_ltd()
    a.plot(p[:30], G[:30], color=BLUE, marker="o", ms=4, lw=2.4, label="LTP")
    a.plot(p[30:], G[30:], color=ORANGE, marker="o", ms=4, lw=2.4, label="LTD")
    a.set_xlabel("Pulse number"); a.set_ylabel("Conductance (µS)"); a.legend(loc="lower center", bbox_to_anchor=(0.42, 0.02), fontsize=14)
    a.set_title("(a) LTP / LTD", loc="left")
    dt, ppf = simulate_ppf()
    b.plot(dt, ppf, color=BLUE, lw=2.6); b.set_xscale("log")
    b.set_xlabel("Interval (ms)"); b.set_ylabel("PPF index (%)"); b.set_title("(b) Paired-pulse", loc="left")
    states = simulate_multilevel()
    for s_ in states:
        c.plot(np.arange(len(s_)), s_, color=BLUE, lw=1.8)
    c.set_xlabel("Read number"); c.set_ylabel("Conductance (a.u.)"); c.set_title("(c) Six levels", loc="left")
    for ax in (a, b, c):
        ax.grid(True, which="major", alpha=.3)
    fig.tight_layout(w_pad=1.2)
    fig.savefig(os.path.join(OUT, "fig9_synaptic.png")); plt.close(fig)

print(f"Single-lobe areas (V·A): " + ", ".join(f"{f} Hz {a_:.2e}" for f, a_ in zip(freqs, areas)))
fmax = max(fine, key=lambda r: r["on_off"])
print(f"Parameter map, 0.1 wt% grid: max ON/OFF {fmax['on_off']:.0f} at {fmax['phi']} wt% (just below the 22 wt% threshold)")
print(f"Drift-diffusion ON/OFF range: {min(r['on_off'] for r in dr):.2f}-{max(r['on_off'] for r in dr):.2f}")
print(f"Saved figures to {os.path.abspath(OUT)}")
