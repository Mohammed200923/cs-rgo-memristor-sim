# CS-rGO Memristor Simulation

Simulation models for printed chitosan-reduced graphene oxide (CS-rGO) memristors on paper substrates, used to choose the composition range for laboratory experiments.

**Status:** computational design study. Every number below is a model output based on the assumed inputs listed in this file. None is a measurement of a device. Laboratory fabrication and testing are planned.

## Results from the current code

| Output | Value | Notes |
|--------|-------|-------|
| ON/OFF ratio, parameter map | 5 at 0 wt% → 315 at 14 wt% → 1,489 at 20 wt% | Rises monotonically up to the assumed threshold |
| Peak loading, parameter map | 20 wt% | Follows from the assumed percolation threshold of 22 wt% |
| Collapse | 2.0 at 22 wt%, 1.7 at 24 wt% | Above the assumed threshold |
| ON/OFF ratio, drift-diffusion | 1.0 at every loading | No peak, so no independent cross-check yet |
| Strukov loop area | 4.4e-8 V·A (1 Hz), 3.0e-9 (5 Hz), 6.9e-9 (20 Hz) | Pinched loops; area not monotonic between 5 and 20 Hz |
| Synaptic curves | LTP 0.82 → 3.73 µS, LTD → 0.31 µS, PPF 169%, 6 levels | Set by the chosen parameters, not predicted by device physics |
| Switching voltage, endurance | Not calculated | The VTEAM time-dependent equations are not solved yet |

## Models

1. **Strukov** (`models/strukov.py`) - linear ion-drift model with a Joglekar window; sinusoidal drive, 1 V, 1/5/20 Hz, 2 cycles.
2. **VTEAM-based parameter map** (`models/vteam.py`) - R_on and R_off set by empirical expressions of φ/φc; ON/OFF = R_off / R_on at each loading.
3. **Drift-diffusion** (`models/drift_diffusion.py`) - 1-D Nernst-Planck solver. The percolation conductivity is computed but does not yet enter the current, so the output does not depend on loading.
4. **Synaptic** (`models/synaptic.py`) - phenomenological exponential LTP/LTD and paired-pulse curves, plus six preset conductance levels with random read noise.

## Main inputs and their sources

"Assumed" means chosen by the author, not taken from a measurement or a cited value.

| Input | Value | Model | Source |
|-------|-------|-------|--------|
| Percolation threshold φc | 22 wt% | Map, drift-diffusion | Assumed; to be checked against Tjong (2012) and measured |
| R_on, R_off at 0 wt% | 5 kΩ, 25 kΩ | Map | Assumed |
| Loading dependence, f = φ/φc | R_on(1 − 0.95 f^0.8), R_off(1 + 40 f^1.5) | Map | Assumed functional form |
| R_on, R_off; thickness; ion mobility | 100 Ω, 25 kΩ; 10 nm; 1e-14 m²/(V·s) | Strukov | Assumed generic values |
| Thickness; ion diffusivity; temperature | 100 nm; 1e-16 m²/s; 300 K | Drift-diffusion | Assumed |
| Conductivity exponent | 1.8 | Drift-diffusion | Assumed |
| LTP/LTD constants; conductance range | 10 and 12 pulses; 0.5-3.9 µS | Synaptic | Assumed |
| PPF amplitude; decay time | 70%; 50 ms | Synaptic | Assumed |
| Multilevel: levels; step; read noise | 6; 50 a.u.; 1.5 a.u. | Synaptic | Assumed |

## How the main values are calculated

- **ON/OFF (map):** R_off / R_on at each loading, 0-24 wt% in 2 wt% steps.
- **Loop area:** |∮ I dV| over the simulated cycles, trapezoidal rule.
- **ON/OFF (drift-diffusion):** effective resistance at 0.01 V divided by that at 1 V, after 1 ms of ion transport.

## Quick start

```bash
pip install -r requirements.txt
python sims/run_all.py        # runs all four models, writes data/simulation_results.csv
python sims/make_figures.py   # rebuilds figures/fig6-fig9 from the models
python tests/test_results.py  # checks the data and the numbers above match the models
```

## Planned model fixes

- Couple the percolation conductivity into the drift-diffusion current.
- Solve the time-dependent VTEAM equations during a ±2 V, 0.1 V/s sweep to obtain switching voltage.
- Scale the Strukov time step with frequency and sweep 1-200 Hz.
- Check the 22 wt% threshold against the literature.
- Run a ±10% sensitivity analysis on every input.

When a model changes, the results table, the figures and `tests/test_results.py` are updated together.

## Structure

```
models/
  strukov.py          # Ion-drift model + window functions
  vteam.py            # Parameter map: R_on, R_off vs rGO loading
  drift_diffusion.py  # Nernst-Planck + percolation conductivity
  synaptic.py         # LTP/LTD, PPF, multilevel states
sims/
  run_all.py          # Runs all 4 models, writes the CSV
  make_figures.py     # Builds figures/fig6-fig9
tests/
  test_results.py     # Data and reported numbers match the models
data/
  simulation_results.csv
figures/
  fig6_strukov.png  fig7_vteam.png  fig8_models.png  fig9_synaptic.png
```
