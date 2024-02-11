from wyvern.data.airfoils import BOEING_VERTOL, NACA0018
from wyvern.utils.airfoil_utils import dat_to_tikz

with open("boeing_vertol.tex", "w") as f:
    f.write(dat_to_tikz(BOEING_VERTOL))

with open("naca0018.tex", "w") as f:
    f.write(dat_to_tikz(NACA0018))
