# Wyvern
Analysis library for Night Fury design in AER406 2024S.

## Setup
Setup is designed to be relatively pain-free.

### Pre-requisites
- Python 3.9 or higher (3.11+ recommended for speedup)
    - I develop on 3.10, so if there are incompatibilities let me know.

### Installation from GitHub
Simply install the package using `pip install git+https://github.com/AER406-SR72/wyvern`. You will need to have Git installed so that you can authenticate with GitHub.

If this doesn't work, install from source (see below).

### Installation from Source
1. Clone this repository.
2. [Optional but recommended] Create a virtual environment. [See here for steps](https://docs.python.org/3/library/venv.html).
3. Install the repo using `pip install -e .` in the root directory of the repo.
4. This will make `wyvern` accessible as a module in your Python environment.

Sometimes, `setuptools` may be outdated. Run `pip install --upgrade setuptools` to fix this.

### Install Flags
`pip install -e .[dev]` -> installs pytest

`pip install -e .[notebook]` -> installs jupyter for notebooks

## Usage
The library is designed to be used as a module. The main entry point is the `wyvern` module, which contains all the functions and classes you need to run the analysis.

### Example: Aerostructual Mass Ratio
For example, we want to use Rassam's mass correlation technique to estimate the aerostructural mass ratio $W_{\text{aerostructure}} / W_0$ of *Night Fury* for use in sizing.

We assume that $ W_{\text{propulsion}} + W_{\text{avionics}} = 400 g$.

```python
from wyvern.sizing import aerostructural_mass_ratio
from wyvern.data.past_designs import BWB_HISTORICAL


fixed_mass = 400 # g
mass_ratio = aerostructural_mass_ratio(BWB_HISTORICAL, fixed_mass)
```

