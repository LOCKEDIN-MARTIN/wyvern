from pathlib import Path

import numpy as np
import pandas as pd

PAYLOADS = pd.read_json(Path(__file__).parent / "sources/payloads.json", orient="index")

# Compute additional metrics
PAYLOADS["ppm"] = PAYLOADS["points"] / PAYLOADS["mass"]
PAYLOADS["volume"] = 4 / 3 * np.pi * (PAYLOADS["diameter"] / 2) ** 3  # mm^3
