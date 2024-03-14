import numpy as np

from wyvern.sizing.parasitic_drag import cfe_turbulent, cfe_xfoil
from wyvern.utils.constants import MU, RHO

chords = np.array([780, 600, 400, 120]) * 1e-3
y_coords = np.array([0, 92.5, 185, 850]) * 1e-3
sections = ["NACA", "NACA", "BOEING", "BOEING"]

v = 10

Re = RHO * v * chords / MU
y_smooth = np.linspace(0, 850, 50) * 1e-3
Re_interp = np.interp(y_smooth, y_coords, Re)

# determine section using nearest neighbor
section = [sections[np.argmin(np.abs(y - y_coords))] for y in y_smooth]

cd_xfoil = cfe_xfoil(Re_interp, section)
cfe_plate = cfe_turbulent(Re_interp)


with open("cfe_output.txt", "w") as f:
    for i in range(len(y_smooth)):
        f.write(
            f"{y_smooth[i]*1e3:.5f} {Re_interp[i]:.5f} {cd_xfoil[i]:.5f} {cfe_plate[i]:.5f}\n"
        )

print("Done.")
