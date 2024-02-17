from pathlib import Path

BOEING_VERTOL = (Path(__file__).parent / "sources/BOEING.dat").read_text()
NACA0018 = (Path(__file__).parent / "sources/NACA0018.dat").read_text()
