"""VTEAM compact model with CS-rGO parameter mapping."""
import numpy as np

def csrgo_params(phi_wt):
    phi_c = 0.22
    phi = phi_wt / 100.0
    if phi < 0.01:
        return 5000, 25000, 1e-15
    elif phi < phi_c:
        frac = phi / phi_c
        R_on = 5000 * (1 - 0.95 * frac**0.8)
        R_off = 25000 * (1 + 40 * frac**1.5)
        mu = 1e-15 * (1 + 500 * frac**2)
        return R_on, R_off, mu
    else:
        excess = (phi - phi_c) / (1 - phi_c)
        return max(10, 250*(1-excess)), max(50, 500*(1-excess**0.5)), 1e-12

def sweep_loading(phi_range=None):
    if phi_range is None:
        phi_range = np.arange(0, 25, 2)
    results = []
    for phi in phi_range:
        R_on, R_off, _ = csrgo_params(phi)
        ratio = R_off / R_on if R_on > 0 else 1
        results.append({"phi": phi, "on_off": ratio, "R_on": R_on, "R_off": R_off})
    return results
