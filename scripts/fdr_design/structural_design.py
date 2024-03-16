# Structural analysis and design script

# Rib layout
# Figuring out where the ribs intersect the spars
# calculating spar taper
# structural loads
# rib shear stresses
# spar bending stresses
# spar shear stresses


from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import rcParams

from wyvern.analysis.structures.abstractions import (
    RibControlPoints,
    SparControlPoints,
    Structure,
)
from wyvern.analysis.structures.plots import do_3d_plots
from wyvern.analysis.structures.rib_calcs import rib_loading, spar_height
from wyvern.data.airfoils import BOEING_VERTOL, NACA0018
from wyvern.utils.constants import G
from wyvern.utils.geom_utils import mirror_verts

# aircraft parameters
M0 = 1.63  # kg
W0 = M0 * G  # N
b = 1.7  # m; span
n = 3.59  # load factor

# Material properties; Balsa wood
s_crush = 1e6  # Pa (crushing strength)
s_rupture = 19e6  # Pa (rupture strength)

# Structure definition
rib = RibControlPoints(
    y=np.array([0, 92.5, 185, 850]),
    c=np.array([780, 600.0, 400, 120]),
    xle=np.array([0, 120.0, 215, 598]),
    twist=np.array([0, 0, 0, 5.0]),
    sections=None,  # auto
)

spar_1 = SparControlPoints(
    y=np.array([0.0, 850.0]),
    x=np.array([195.0, 628.0]),
)
spar_2 = SparControlPoints(
    y=np.array([185.0, 850.0]),
    x=np.array([515.0, 688.0]),
)

rib_t_inches = np.array([1 / 4, 1 / 16, 1 / 16, 1 / 16, 1 / 16, 1 / 16, 1 / 16, 1 / 16])

# Rib Locations
rib_y = mirror_verts(np.array([0, 92.5, 185, 318, 451, 584, 717, 850])) * 1e-3  # m

structure = Structure.from_structure(rib_y, rib, rib_t_inches, spar_1, spar_2)

print(structure.rib.twist)

num_ribs = len(rib_y)


# Lift loading
# - Each rib carries a portion of the lift
# - The portion is equal to the integral of the lift distribution halfway between itself and its neighbours

# data
lift_path = Path(__file__).parent.parent.parent / "wyvern/data/sources/lift_dists"
lift_data = np.genfromtxt(lift_path / "Full_cruise_L.csv", delimiter=",", skip_header=1)
# normalize lift data
T = np.trapz(lift_data[:, 1], lift_data[:, 0])
lift_data[:, 1] = W0 * lift_data[:, 1] / T


def ell(y):
    # real lift distr
    return np.interp(y, lift_data[:, 0], lift_data[:, 1]) * n


rib_force = rib_loading(ell, rib_y)

# Plotting
do_3d_plots(structure)

# latex plots
rcParams["text.usetex"] = True
# use computer modern serif font for all text
rcParams["font.family"] = "serif"

# Plots
fig, axs = plt.subplots(2, 1, tight_layout=True, sharex=True, figsize=(6, 6))

for i in range(num_ribs):
    axs[0].plot(
        [rib_y[i], rib_y[i]],
        [structure.rib.xle[i], structure.rib.xle[i] + structure.rib.c[i]],
        "k-",
    )
axs[0].plot(rib_y, structure.spars[0].x, color="forestgreen", label="Main Spar")
axs[0].plot(rib_y, structure.spars[1].x, color="darkseagreen", label="Secondary Spar")
axs[0].invert_yaxis()

ax1_twin = axs[1].twinx()
ax1_twin.bar(rib_y, rib_force, width=0.05, color="C1", alpha=0.8, edgecolor="k")
axs[1].fill_between(
    np.linspace(min(rib_y), max(rib_y), 100),
    ell(np.linspace(min(rib_y), max(rib_y), 100)),
    color="C0",
    alpha=0.5,
)
axs[1].plot(
    np.linspace(min(rib_y), max(rib_y), 100),
    ell(np.linspace(min(rib_y), max(rib_y), 100)),
    color="C0",
)
axs[0].set_ylabel("Chordwise position (m)")
axs[0].set_title("Spar and Rib layout", fontsize=10)
axs[0].legend()
axs[0].grid(linewidth=0.5, alpha=0.5)

axs[1].set_title(f"Structural Loading (n = {n:.2f})", fontsize=10)
axs[1].set_xlabel("y (mm)")
ax1_twin.set_ylabel("Rib Load (N)", color="C1")
axs[1].set_ylabel("Lift Distribution (N/m)", color="C0")
# change ticks and axis colors similarly to MATLAB
axs[1].tick_params(axis="y", colors="C0")
ax1_twin.tick_params(axis="y", colors="C1")
axs[1].grid(linewidth=0.5, alpha=0.5)
axs[1].set_ylim(0, max(ell(rib_y)) * 1.1)

axs[1].set_xticks(rib_y)
axs[1].set_xticklabels([f"{y*1000:.0f}" for y in rib_y], rotation=45)

plt.tight_layout()
plt.savefig("rib_loads.pdf", bbox_inches="tight")

plt.show()
