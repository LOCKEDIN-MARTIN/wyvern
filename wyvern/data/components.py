from pathlib import Path

import pandas as pd

# run this automatically on import (messy, but it works)
# Turn into dataframe (do indices correctly)
ALL_COMPONENTS = pd.read_json(
    Path(__file__).parent / "sources/components.json", orient="index"
)

AVIONICS_COMPONENTS = ALL_COMPONENTS[ALL_COMPONENTS["category"] == "Avionics"]
PROPULSION_COMPONENTS = ALL_COMPONENTS[ALL_COMPONENTS["category"] == "Propulsion"]
