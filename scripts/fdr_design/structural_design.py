# Structural analysis and design script

# Rib layout
# Figuring out where the ribs intersect the spars
# calculating spar taper
# structural loads
# rib shear stresses
# spar bending stresses
# spar shear stresses


import numpy as np
from matplotlib import pyplot as plt

from wyvern.analysis.rib_analysis.calcs import rib_loading, spar_height
from wyvern.analysis.rib_analysis.plots import rib_spar_structure_plot
from wyvern.data.airfoils import BOEING_VERTOL, NACA0018
from wyvern.utils.constants import G
from wyvern.utils.geom_utils import mirror_verts

# aircraft parameters
M0 = 1.63  # kg
W0 = M0 * G  # N
b = 1.7  # m; span
n = 3  # load factor

# Material properties; Balsa wood
s_crush = 1e6  # Pa (crushing strength)

# Wing geometry, defined via control points
# Span stations
ctrl_y = mirror_verts(np.array([0, 92.5, 185, 850])) * 1e-3  # m
# Wing chord
ctrl_c = mirror_verts(np.array([780, 600, 400, 120]), negate=False) * 1e-3  # m
# Leading Edge x-coordinates
ctrl_xle = mirror_verts(np.array([0, 0.120, 0.215, 0.598]), negate=False)  # m
ctrl_twist = np.array([7, 0, 7])  # degrees (for some reason, -ve is +ve)

# Rib Locations
rib_y = mirror_verts(np.array([0, 92.5, 185, 318, 451, 584, 717, 850])) * 1e-3  # m
# Rib thickness
rib_t = (
    mirror_verts(
        np.array([1 / 8, 1 / 16, 1 / 16, 1 / 16, 1 / 16, 1 / 16, 1 / 16, 1 / 16]),
        negate=False,
    )
    * 1e-3
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

twist = np.interp(rib_y, np.array([-850, 0, 850]) * 1e-3, ctrl_twist)


# Lift loading
# - Each rib carries a portion of the lift
# - The portion is equal to the integral of the lift distribution halfway between itself and its neighbours
def ell(y):
    # Elliptical lift distribution
    return 4 * n * W0 / (np.pi * b) * np.sqrt(1 - (2 * y / b) ** 2)


rib_force = rib_loading(ell, rib_y)
rib_s_stop, rib_s_bot = spar_height(rib_y, rib_c, rib_xle, spar_x, twist, rib_sections)
rib_s2_stop, rib_s2_bot = spar_height(
    rib_y, rib_c, rib_xle, spar_2x, twist, rib_sections
)

# plot 3D views of spar and rib layout
rib_spar_structure_plot(
    [rib_s_stop, rib_s2_stop],
    [rib_s_bot, rib_s2_bot],
    rib_y,
    rib_c,
    rib_xle,
    [spar_x, spar_2x],
    twist,
    rib_sections,
)


with open("rib_spar_layout.txt", "w") as f:
    f.write("y\t x1\t z1_top\t z1_bot\t h1\tx2\t z2_top\t z2_bot\t h2\t\n")
    for i in range(num_ribs):
        f.write(
            f"{rib_y[i]*1000:.2f}\t {spar_x[i]*1000:.2f}\t {rib_s_stop[i]*1000:.2f}\t {rib_s_bot[i]*1000:.2f}\t {1000*(rib_s_stop[i] - rib_s_bot[i]):.1f} \t"
            f"{spar_2x[i]*1000:.2f}\t {rib_s2_stop[i]*1000:.2f}\t {rib_s2_bot[i]*1000:.2f}\t {1000*(rib_s2_stop[i] - rib_s2_bot[i]):.1f}\n"
        )
#
plt.savefig("3d_structure.pdf")

# switch to 2D view
plt.gca().view_init(elev=0, azim=0)
plt.subplots_adjust(left=-0.6, right=1.6, top=1.6, bottom=-0.6)
plt.savefig("2d_structure.pdf")

# side shot
plt.gca().view_init(elev=0, azim=90)
plt.savefig("side_structure.png", dpi=300)

# Plots
fig, axs = plt.subplots(3, 1, tight_layout=True, figsize=(8, 8))

for i in range(num_ribs):
    axs[0].plot([rib_y[i], rib_y[i]], [rib_xle[i], rib_xle[i] + rib_c[i]], "k-")
axs[0].plot(rib_y, spar_x, color="C0", label="Main Spar")
axs[0].plot(rib_y, spar_2x, color="C1", label="Secondary Spar")

ax1_twin = axs[1].twinx()
ax1_twin.bar(rib_y, rib_force, width=0.05)
axs[1].plot(
    np.linspace(min(rib_y), max(rib_y), 100),
    ell(np.linspace(min(rib_y), max(rib_y), 100)),
    "r-",
)

axs[2].plot(rib_y, rib_s_stop, "C0", label="Main Spar")
axs[2].plot(rib_y, rib_s_bot, "C0", label="_")
axs[2].plot(rib_y, rib_s2_stop, "C1", label="Secondary Spar")
axs[2].plot(rib_y, rib_s2_bot, "C1", label="_")


axs[0].set_xlabel("Spanwise position (m)")
axs[0].set_ylabel("Chordwise position (m)")
axs[0].set_title("Spar and Rib layout")
axs[0].grid(True)
axs[0].legend()

axs[1].set_title("Structural Loading (n = 3)")
axs[1].set_xlabel("Spanwise position (m)")
ax1_twin.set_ylabel("Rib Load (N)", color="C0")
axs[1].set_ylabel("Lift Distribution (N/m)", color="r")
axs[1].grid(True)

axs[2].set_title("Spar Height")
axs[2].set_xlabel("Spanwise position (m)")
axs[2].set_ylabel("Height (m)")
axs[2].legend()
axs[2].grid(True)
axs[2].axis("equal")
plt.savefig("rib_spar_layout.pdf")

plt.show()
