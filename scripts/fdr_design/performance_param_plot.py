import numpy as np
from matplotlib import pyplot as plt
from matplotlib import rcParams

from wyvern.data.propellers import PROP_8X8, PROP_9X6, PROP_10X5
from wyvern.performance.models import QuadraticLDModel
from wyvern.performance.plotting import plot_drag_polar, power_plot, thrust_plot
from wyvern.utils.constants import RHO

ld_model = QuadraticLDModel(c_d0=0.0320, e_inviscid=0.95, K=0.45, aspect_ratio=5.106458)
ws = 2.874 * 9.81

# plt.style.use("dark_background")

rcParams["text.usetex"] = True
# use computer modern serif font for all text
rcParams["font.family"] = "serif"

# max climb power
v_rcmax = np.sqrt(2 * ws / (RHO * np.sqrt(3 * ld_model.c_d0 / ld_model.kappa)))

plt.figure(figsize=(9, 4))
plt.subplot(122)
v_climb = power_plot(ld_model, ws, 0.56595, PROP_9X6)
plt.title("Power Performance, 9x6E APC Propeller", fontsize=10)
plt.axvline(x=v_rcmax, color="C5", linestyle="--")
plt.axvline(x=v_climb, color="C6", linestyle="--")
plt.text(
    v_rcmax + 0.1,
    16,
    "v$_{RC, \mathrm{max}}$" + f" = {v_rcmax:.2f} m/s",
    ha="left",
    va="bottom",
    rotation=90,
    color="C5",
)
plt.text(
    v_climb + 0.1,
    25,
    "v$_{\mathrm{climb}}$" + f" = {v_climb:.2f} m/s",
    ha="left",
    va="bottom",
    rotation=90,
    color="C6",
)

plt.subplot(121)
thrust_plot(ld_model, ws, 0.56595, PROP_9X6)
plt.title("Thrust Performance, 9x6E APC Propeller", fontsize=10)
plt.axvline(x=ld_model.v_ldmax(ws), color="C2", linestyle="--")
plt.axvline(x=10, color="C3", linestyle="--")
plt.axvline(x=7, color="C4", linestyle="--")
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
    color="C3",
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

plot_drag_polar(ld_model)
plt.savefig("drag_polar.pdf", bbox_inches="tight")

# plot L/D with CL, and L^1.5/D

cL_range = np.linspace(0, 1.2, 100)
cD_range = ld_model.c_D(cL_range)
ld = cL_range / cD_range
ld_15 = cL_range**1.5 / cD_range
plt.figure(figsize=(4, 3))
plt.plot(cL_range, ld, label="$$C_L/C_D$$")
plt.plot(cL_range, ld_15, label="$$C_L^{1.5}/C_D$$")

plt.xlabel("$C_L$")
plt.ylabel("Dimensionless")

plt.grid(linewidth=0.5, alpha=0.5)
plt.title("Performance parameters")
plt.legend()
plt.savefig("clcd15.pdf", bbox_inches="tight")
