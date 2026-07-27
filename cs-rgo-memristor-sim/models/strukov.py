"""Strukov linear ion-drift memristor model with window functions."""
import numpy as np
from scipy.integrate import solve_ivp

def joglekar_window(x, p=1):
    return 1 - (2*x - 1)**(2*p)

def biolek_window(x, i, p=1):
    return 1 - (x - 1)**(2*p) if i >= 0 else 1 - x**(2*p)

def simulate_iv(freq=1.0, amplitude=1.0, cycles=2, R_on=100, R_off=25000, D=10e-9, mu_v=1e-14, x0=0.5, window="joglekar", dt=1e-4):
    T = cycles / freq
    t = np.arange(0, T, dt)
    v = amplitude * np.sin(2 * np.pi * freq * t)
    x = np.zeros_like(t); x[0] = x0
    for n in range(len(t)-1):
        R = R_on * x[n] + R_off * (1 - x[n])
        i_n = v[n] / R
        w = joglekar_window(x[n]) if window == "joglekar" else biolek_window(x[n], i_n)
        dxdt = mu_v * R_on / D**2 * i_n * w
        x[n+1] = np.clip(x[n] + dxdt * dt, 0.001, 0.999)
    R_arr = R_on * x + R_off * (1 - x)
    i_arr = v / R_arr
    return t, v, i_arr, x, R_arr

def compute_loop_area(v, i):
    return np.abs(np.trapezoid(i, v))
