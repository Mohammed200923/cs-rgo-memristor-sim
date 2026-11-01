# CS-rGO Memristor Simulation

Simulation models for printed chitosan-reduced graphene oxide (CS-rGO) memristors on paper, used to choose the composition range for laboratory experiments.

**Status:** computational design study. All values are model outputs based on assumed inputs; none is a measurement.

Everything is in the [`cs-rgo-memristor-sim/`](cs-rgo-memristor-sim/) folder:

- [README](cs-rgo-memristor-sim/README.md) - results, model inputs and their sources, how each value is calculated
- [`models/`](cs-rgo-memristor-sim/models/) - the four models
- [`figures/`](cs-rgo-memristor-sim/figures/) - Fig. 6-9 of the project form, built from the models

```bash
cd cs-rgo-memristor-sim
pip install -r requirements.txt
python sims/run_all.py        # run all models, write data/simulation_results.csv
python sims/make_figures.py   # rebuild the figures
python tests/test_results.py  # check data and reported numbers match the models
```
