from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import rcParams
from scipy.optimize import curve_fit

from wyvern.data.airfoils import BOEING_VERTOL, NACA0018
from wyvern.sizing.parasitic_drag import _drag_integrand, cd0_buildup, cfe_turbulent
from wyvern.utils.constants import MU, RHO
from wyvern.utils.geom_utils import mirror_verts

# MPL settings
rcParams["text.usetex"] = True
# use computer modern serif font for all text
rcParams["font.family"] = "serif"


# aircraft parameters
ctrl_y = mirror_verts(np.array([0, 92.5, 185, 850])) * 1e-3  # m
# Wing chord
ctrl_c = mirror_verts(np.array([780, 600, 400, 120]), negate=False) * 1e-3  # m

Sref = 0.56595
S_winglet = 0.04
v_analysis = 10

# load reference data (10 m/s)
xfoil_ref_data = np.loadtxt(
    Path(__file__).parent.parent.parent / "wyvern/data/sources/xfoil_cf_10ms.dat"
)


sections = [BOEING_VERTOL] * 2 + [NACA0018] * 3 + [BOEING_VERTOL] * 2
sweeps = np.array([27, 27, 0, 0, 0, 27, 27])

CD0_wb, wetted_area = cd0_buildup(ctrl_y, ctrl_c, sections, sweeps, v_analysis, Sref)

CD0_winglet = (
    cfe_turbulent(RHO * v_analysis * ctrl_c[-1] / MU) * S_winglet / Sref
)  # use k = 1 for winglet
CD0_lg = 0.00821

print(f"CD0 wb: {CD0_wb:.5f}")
print(f"CD0 winglet: {CD0_winglet:.5f}")
print(f"Wetted Area: {wetted_area:.5f}")


# Plots

y_series = np.linspace(0, 850, 200) * 1e-3
xfoil_ref_cd = np.interp(y_series, xfoil_ref_data[:, 0] / 1000, xfoil_ref_data[:, 2])
data = [
    _drag_integrand(y, ctrl_y, ctrl_c, sections, sweeps, v_analysis, all_outputs=True)
    for y in y_series
]

c_i = np.array([d[0] for d in data])
sweep_i = np.array([d[1] for d in data])
tcmax = np.array([d[2] for d in data])
s = np.array([d[3] for d in data])
Re_i = np.array([d[4] for d in data])
cf_i = np.array([d[5] for d in data])
k_i = np.array([d[6] for d in data])
Q_i = np.array([d[7] for d in data])

CD0_xfoil = np.trapz(xfoil_ref_cd * s / (wetted_area / 2), y_series)
print(f"CD0 xfoil: {CD0_xfoil:.5f}")

plt.figure(figsize=(8, 3.5))
plt.plot(y_series * 1e3, Re_i, color="r")
plt.title(f"Zero-Lift Drag Along Wing, $v = {v_analysis}$ m/s", fontsize=10)
plt.xlabel("y (mm)")
plt.ylabel("Reynolds Number", color="r")
plt.grid(linewidth=0.5, alpha=0.5)
plt.gca().tick_params(axis="y", colors="r")

plt.twinx()
plt.plot(
    y_series * 1e3,
    k_i * cf_i * Q_i * wetted_area / Sref,
    color="k",
    label="$k(y) c_f(y) Q(y) \\times S_{\mathrm{wet}}/S_{\mathrm{ref}}$",
)
plt.plot(y_series * 1e3, xfoil_ref_cd, "--", color="k", label="XFOIL $C_{d0}(y)$")
plt.ylabel("Drag Coefficient", color="k")
plt.legend(loc="upper center")

plt.xticks(
    [
        0,
        92.5,
        185,
        318,
        451,
        584,
        717,
        850,
    ]
)
plt.xlim(0, 850)

# colour numbers like MATLAB
plt.gca().tick_params(axis="y", colors="k")

plt.savefig("cd0_buildup.pdf", bbox_inches="tight")

plt.show()

# plot cd0 vs speed

v_series = np.linspace(1, 15, 100)

cd0_series = [
    cd0_buildup(ctrl_y, ctrl_c, sections, sweeps, v, Sref)[0]
    + cfe_turbulent(RHO * v_analysis * ctrl_c[-1] / MU) * S_winglet / Sref
    + CD0_lg
    + 0.005
    for v in v_series
]


# fit power curve
def power_curve(x, a, b):
    return a * x**b


fit = curve_fit(power_curve, v_series, cd0_series, p0=[0.01, -0.01])

print(f"CD0 = {fit[0][0]:.4f} * v^{fit[0][1]:.4f}")

plt.figure(figsize=(6, 3))
plt.plot(v_series, cd0_series, label="Data", color="k")
plt.plot(v_series, power_curve(v_series, *fit[0]), "--r", label="Fit")
plt.title("$C_{D0}$ vs Speed", fontsize=10)
plt.xlabel("Speed (m/s)")
plt.ylabel("$C_{D0}$")
plt.grid(linewidth=0.5, alpha=0.5)
plt.legend(frameon=False)

plt.savefig("cd0_vs_speed.pdf", bbox_inches="tight")
plt.show()
