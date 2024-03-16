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

# Wing geometry, defined via control points
# Span stations
ctrl_y = mirror_verts(np.array([0, 92.5, 185, 850])) * 1e-3  # m
# Wing chord
ctrl_c = mirror_verts(np.array([780, 600, 400, 120]), negate=False) * 1e-3  # m
# Leading Edge x-coordinates
ctrl_xle = mirror_verts(np.array([0, 0.120, 0.215, 0.598]), negate=False)  # m
ctrl_twist = mirror_verts(np.array([0, 0, 0, 5]), negate=False)  # deg

# Rib Locations
rib_y = mirror_verts(np.array([0, 92.5, 185, 318, 451, 584, 717, 850])) * 1e-3  # m
# Rib thickness
rib_t = (
    mirror_verts(
        np.array([1 / 4, 1 / 16, 1 / 16, 1 / 16, 1 / 16, 1 / 16, 1 / 16, 1 / 16]),
        negate=False,
    )
    * 1e-3
    * 25.4
)  # m


num_ribs = len(rib_y)

# Spar geometry
# - Spar goes from c/4 centerline to c/4 tip
# - Height of spar matches intersection point with the ribs (tapered)
# - Spar is a box beam, balsa wood

ctrl_spar_y = mirror_verts(np.array([0, 850])) * 1e-3  # m
ctrl_spar_x = (
    mirror_verts(np.array([195, 628]), negate=False) * 1e-3
)  # m; (c/4 centerline to c/4 tip)

# secondary spar
ctrl_spar2_y = np.array([185, 850]) * 1e-3  # m
ctrl_spar2_x = np.array([515, 688]) * 1e-3  # m
# 3c/4 from wings to tip

# hack: linear extrapolate from y=185 to y=0
ctrl_spar2_x = np.insert(
    ctrl_spar2_x,
    0,
    ctrl_spar2_x[0]
    + ((ctrl_spar2_x[1]) - (ctrl_spar2_x[0]))
    / (ctrl_spar2_y[1] - ctrl_spar2_y[0])
    * (0 - ctrl_spar2_y[0]),
)
ctrl_spar2_y = np.insert(ctrl_spar2_y, 0, 0)

ctrl_spar2_y = mirror_verts(ctrl_spar2_y)
ctrl_spar2_x = mirror_verts(ctrl_spar2_x, negate=False)

# Interpolate to rib locations
# Chord at each rib
rib_c = np.interp(rib_y, ctrl_y, ctrl_c)
# Leading edge x-coordinates at each rib
rib_xle = np.interp(rib_y, ctrl_y, ctrl_xle)
# Sections at each rib (hardcoded - 3 center ribs with NACA0018, 6 outer ribs with BOEING_VERTOL)
rib_sections = [BOEING_VERTOL] * 6 + [NACA0018] * 3 + [BOEING_VERTOL] * 6
# Spar intersection x-coordinates
spar_x = np.interp(rib_y, ctrl_spar_y, ctrl_spar_x)
spar_2x = np.interp(rib_y, ctrl_spar2_y, ctrl_spar2_x)

twist = np.interp(
    rib_y, np.array([-850, -185, -92.5, 0, 92.5, 185, 850]) * 1e-3, ctrl_twist
)
# control surface points
twist_elevon = np.interp([0.451, 0.717], ctrl_y, ctrl_twist)


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
rib_s_stop, rib_s_bot = spar_height(rib_y, rib_c, rib_xle, spar_x, twist, rib_sections)
rib_s2_stop, rib_s2_bot = spar_height(
    rib_y, rib_c, rib_xle, spar_2x, twist, rib_sections
)

# Plotting
do_3d_plots(
    rib_y,
    rib_c,
    rib_xle,
    spar_x,
    spar_2x,
    twist,
    rib_sections,
    rib_s_stop,
    rib_s2_stop,
    rib_s_bot,
    rib_s2_bot,
)

# latex plots
rcParams["text.usetex"] = True
# use computer modern serif font for all text
rcParams["font.family"] = "serif"

# Plots
fig, axs = plt.subplots(2, 1, tight_layout=True, sharex=True, figsize=(6, 6))

for i in range(num_ribs):
    axs[0].plot([rib_y[i], rib_y[i]], [rib_xle[i], rib_xle[i] + rib_c[i]], "k-")
axs[0].plot(rib_y, spar_x, color="forestgreen", label="Main Spar")
axs[0].plot(rib_y, spar_2x, color="darkseagreen", label="Secondary Spar")
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
