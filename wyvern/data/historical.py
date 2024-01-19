from pathlib import Path

import pandas as pd

# run this automatically on import (messy, but it works)
ALL_HISTORICAL = pd.read_excel(
    Path(__file__).parent / "sources/AER406_hist_2024_modified.xlsx"
)

# Balsa Planes
BALSA_HISTORICAL = ALL_HISTORICAL[ALL_HISTORICAL["Construction"] == "Balsa"]

# BWB & Balsa Planes
BWB_HISTORICAL = BALSA_HISTORICAL[(BALSA_HISTORICAL["Config"] == "BWB")]

# Rassam Correlation
RASSAM_CORRELATIONS = ALL_HISTORICAL.iloc[[5, 6, 7, 8, 10, 30]]
