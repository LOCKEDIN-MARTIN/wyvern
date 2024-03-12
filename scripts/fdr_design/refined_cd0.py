from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt

from wyvern.data.airfoils import BOEING_VERTOL, NACA0018
from wyvern.sizing.parasitic_drag import _drag_integrand, cd0_buildup
from wyvern.utils.geom_utils import mirror_verts

# aircraft parameters
ctrl_y = mirror_verts(np.array([0, 92.5, 185, 850])) * 1e-3  # m
# Wing chord
ctrl_c = mirror_verts(np.array([780, 600, 400, 120]), negate=False) * 1e-3  # m

Sref = 0.566
v_analysis = 10

# load reference data (10 m/s)
xfoil_ref_data = np.loadtxt(
    Path(__file__).parent.parent.parent / "wyvern/data/sources/xfoil_cf_10ms.dat"
)


sections = [BOEING_VERTOL] * 2 + [NACA0018] * 3 + [BOEING_VERTOL] * 2
sweeps = np.array([30, 30, 0, 0, 0, 30, 30])

CD0, wetted_area = cd0_buildup(ctrl_y, ctrl_c, sections, sweeps, v_analysis, Sref)

print(f"CD0: {CD0:.4f}")
print(f"Wetted Area: {wetted_area:.4f}")


# Plots

y_series = np.linspace(0, 850, 200) * 1e-3


xfoil_ref_cd = np.interp(y_series, xfoil_ref_data[:, 0], xfoil_ref_data[:, 2])

data = [
    _drag_integrand(y, ctrl_y, ctrl_c, sections, sweeps, v_analysis, all_outputs=True)
    for y in y_series
]

c_i = [d[0] for d in data]
sweep_i = [d[1] for d in data]
tcmax = [d[2] for d in data]
s = [d[3] for d in data]
Re_i = [d[4] for d in data]
cf_i = [d[5] for d in data]
k_i = [d[6] for d in data]

plt.figure(figsize=(12, 4))
plt.plot(y_series, Re_i, color="C0")
plt.title("Skin Drag")
plt.xlabel("y (m)")
plt.ylabel("Reynolds Number", color="C0")
plt.grid()

plt.twinx()
plt.plot(y_series, cf_i, color="C1")
plt.ylabel("Skin Friction Coefficient", color="C1")

plt.savefig("cd0_buildup.pdf")

plt.show()

# plot cd0 vs speed

v_series = np.linspace(1, 15, 100)

cd0_series = [
    cd0_buildup(ctrl_y, ctrl_c, sections, sweeps, v, Sref)[0] for v in v_series
]

plt.figure()
plt.plot(v_series, cd0_series)
plt.title("CD0 vs Speed")
plt.xlabel("Speed (m/s)")
plt.ylabel("CD0")
plt.grid()

plt.savefig("cd0_vs_speed.pdf")
plt.show()
