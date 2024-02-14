from wyvern.data.airfoils import BOEING_VERTOL
from wyvern.utils.airfoil_utils import dat_to_tikz, naca_4d_to_tikz

with open("boeing_vertol.tex", "w") as f:
    f.write(dat_to_tikz(BOEING_VERTOL))

with open("naca0018.tex", "w") as f:
    f.write(naca_4d_to_tikz("0018", 30))
