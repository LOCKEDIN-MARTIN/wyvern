from pathlib import Path

import numpy as np

BOEING_VERTOL = np.loadtxt(Path(__file__).parent / "sources/BOEING.dat")
NACA0018 = np.loadtxt(Path(__file__).parent / "sources/NACA0018.dat")
