# CS-rGO Memristor Simulation

Simulation-guided design of printed chitosan-reduced graphene oxide memristors on paper substrates for sustainable neuromorphic computing.

## Key Results

| Metric | Value |
|--------|-------|
| Optimal loading | ~14 wt% rGO |
| Fabrication window | 8-16 wt% |
| Percolation collapse | >22 wt% |
| Switching voltage | <1 V |
| Conductance states | 6 |
| Cross-validation | Two independent models agree |

## Models

1. **Strukov** - validates memristive fingerprint (pinched hysteresis, ~154,000x collapse)
2. **VTEAM** - predicts optimal composition by sweeping 0-24 wt%
3. **Drift-diffusion** - independent physics-based confirmation (no shared parameters)
4. **Synaptic** - LTP/LTD, paired-pulse facilitation, multilevel analog states

## Quick Start

```bash
pip install -r requirements.txt
python sims/run_all.py
```

## Structure

```
models/
  strukov.py          # Ion-drift model + window functions
  vteam.py            # VTEAM + CS-rGO parameter mapping
  drift_diffusion.py  # Nernst-Planck + percolation
  synaptic.py         # LTP/LTD, PPF, multilevel states
sims/
  run_all.py          # Runs all 4 stages, outputs CSV
data/
  simulation_results.csv
```

## License

MIT
