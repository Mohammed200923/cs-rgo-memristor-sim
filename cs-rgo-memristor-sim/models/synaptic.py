"""Synaptic behavior simulation: LTP/LTD, PPF, multilevel states."""
import numpy as np

def simulate_ltp_ltd(n_p=30, n_d=30, G_min=0.5, G_max=3.9, tau_p=10, tau_d=12):
    p = np.arange(1, n_p+1); d = np.arange(n_p+1, n_p+n_d+1)
    G_ltp = G_min + (G_max-G_min)*(1-np.exp(-p/tau_p))
    G_ltd = G_ltp[-1]*np.exp(-(d-n_p)/tau_d)
    return np.concatenate([p,d]), np.concatenate([G_ltp, G_ltd])

def simulate_ppf(dt=None, A=70, tau=50):
    if dt is None: dt = np.logspace(0, 3, 40)
    return dt, 100 + A*np.exp(-dt/tau)

def simulate_multilevel(n_states=6, n_reads=36, noise=1.5, G_base=30, G_step=50):
    return np.array([G_base+i*G_step+np.random.normal(0,noise,n_reads) for i in range(n_states)])
