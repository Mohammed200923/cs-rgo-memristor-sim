"""1-D Nernst-Planck drift-diffusion solver with percolation."""
import numpy as np
from scipy.integrate import solve_ivp

def percolation_conductivity(phi_wt, phi_c=22.0, t_exp=1.8):
    phi, pc = phi_wt/100.0, phi_c/100.0
    if phi <= 0: return 1e-6
    elif phi < pc: return 1e-4 + 1.0 * ((phi/pc)**t_exp)
    else: return 10.0 * ((phi-pc)/(1-pc))**0.5

def drift_diffusion_solve(phi_wt, V_app=1.0, L=100e-9, N=50, D_ion=1e-16, z=1, T_temp=300):
    dx = L/N; kB=1.38e-23; q=1.6e-19
    sigma = percolation_conductivity(phi_wt)
    mu_ion = D_ion*z*q/(kB*T_temp)
    E = V_app/L; c0 = np.ones(N)*1e20
    def dcdt(t, c):
        dc = np.zeros_like(c)
        for i in range(1, N-1):
            dc[i] = D_ion*(c[i+1]-2*c[i]+c[i-1])/dx**2 - mu_ion*E*(c[i+1]-c[i-1])/(2*dx)
        return dc
    sol = solve_ivp(dcdt, (0, 1e-3), c0, method="Radau", max_step=1e-5)
    c_final = sol.y[:, -1]
    j = z*q*(mu_ion*E*c_final.mean())
    R_eff = V_app/(j*1e-12) if j != 0 else 1e12
    return R_eff, sigma, c_final

def sweep_loading_physics(phi_range=None):
    if phi_range is None:
        phi_range = np.arange(0, 25, 2)
    results = []
    for phi in phi_range:
        R_on, _, _ = drift_diffusion_solve(phi, V_app=1.0)
        R_off, _, _ = drift_diffusion_solve(phi, V_app=0.01)
        ratio = R_off/R_on if R_on > 0 else 1
        results.append({"phi": phi, "on_off": min(ratio, 1e7)})
    return results
