import numpy as np
from matplotlib import pyplot as plt
from matplotlib import rcParams

from wyvern.data.propellers import PROP_8X8, PROP_9X6, PROP_10X5
from wyvern.performance.models import QuadraticLDModel
from wyvern.performance.plotting import plot_drag_polar, power_plot, thrust_plot
from wyvern.utils.constants import RHO

ld_model = QuadraticLDModel(
    c_d0=0.02959, e_inviscid=0.95, K=0.45, aspect_ratio=5.106458
)
ws = 2.874 * 9.81

# plt.style.use("dark_background")

rcParams["text.usetex"] = True
# use computer modern serif font for all text
rcParams["font.family"] = "serif"

# max climb power
v_rcmax = np.sqrt(2 * ws / (RHO * np.sqrt(3 * ld_model.c_d0 / ld_model.kappa)))

plt.figure(figsize=(9, 4))
plt.subplot(122)
v_climb, v_max = power_plot(ld_model, ws, 0.56595, PROP_9X6)
plt.title("Power Performance, 9x6E APC Propeller", fontsize=10)
plt.axvline(x=v_rcmax, color="C1", linestyle="--", linewidth=1)
plt.axvline(x=v_climb, color="C3", linestyle="--", linewidth=1)
plt.axvline(x=v_max, color="C5", linestyle="--", linewidth=1)
plt.text(
    v_rcmax + 0.1,
    16,
    "v$_{RC, \mathrm{max}}$" + f" = {v_rcmax:.2f} m/s",
    ha="left",
    va="bottom",
    rotation=90,
    color="C1",
)
plt.text(
    v_climb + 0.1,
    25,
    "v$_{\mathrm{climb}}$" + f" = {v_climb:.2f} m/s",
    ha="left",
    va="bottom",
    rotation=90,
    color="C3",
)
plt.text(
    v_max - 0.1,
    30,
    "v$_{\mathrm{max}}$" + f" = {v_max:.2f} m/s",
    ha="right",
    va="bottom",
    rotation=90,
    color="C5",
)

plt.subplot(121)
thrust_plot(ld_model, ws, 0.56595, PROP_9X6)
plt.title("Thrust Performance, 9x6E APC Propeller", fontsize=10)
plt.axvline(x=ld_model.v_ldmax(ws), color="C2", linestyle="--", linewidth=1)
plt.axvline(x=10, color="C0", linestyle="--", linewidth=1)
plt.axvline(x=7, color="C4", linestyle="--", linewidth=1)
plt.text(
    ld_model.v_ldmax(ws) - 0.1,
    2.5,
    "v$_{LD, \mathrm{max}}$" + f" = {ld_model.v_ldmax(ws):.2f} m/s",
    ha="right",
    va="bottom",
    rotation=90,
    color="C2",
)
plt.text(
    10.1,
    2.5,
    "v$_{\mathrm{cruise}}$ = 10 m/s",
    ha="left",
    va="bottom",
    rotation=90,
    color="C0",
)
plt.text(
    6.9,
    2.5,
    "v$_{\mathrm{stall}}$ = 7 m/s",
    ha="right",
    va="bottom",
    rotation=90,
    color="C4",
)
plt.tight_layout()
plt.savefig("power_thrust_performance.pdf", bbox_inches="tight")

plt.figure(figsize=(8, 3))
plt.subplot(121)
plot_drag_polar(ld_model)


# plot L/D with CL, and L^1.5/D

cL_range = np.linspace(0, 1.2, 100)
cD_range = ld_model.c_D(cL_range)
ld = cL_range / cD_range
ld_15 = cL_range**1.5 / cD_range
plt.subplot(122)
plt.plot(cL_range, ld, "-k", label="$$C_L/C_D$$")

plt.xlabel("$C_L$")
plt.ylabel("$C_L/C_D$")

plt.grid(linewidth=0.5, alpha=0.5)
plt.title("Drag Efficiency Variation", fontsize=10)

plt.tight_layout()
plt.savefig("drag_polar.pdf", bbox_inches="tight")
