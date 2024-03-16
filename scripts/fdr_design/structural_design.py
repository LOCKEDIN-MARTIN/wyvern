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

from wyvern.analysis.structures.abstractions import (
    RibControlPoints,
    SparControlPoints,
    Structure,
)
from wyvern.analysis.structures.plots import do_3d_plots, rib_loading_plot
from wyvern.analysis.structures.rib_calcs import rib_loading
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
y = mirror_verts(np.array([0, 92.5, 185, 318, 451, 584, 717, 850])) * 1e-3  # m
structure = Structure.from_structure(y, rib, rib_t_inches, spar_1, spar_2)

# Lift loading
# - Each rib carries a portion of the lift
# - The portion is equal to the integral of the lift distribution halfway between itself and its neighbours

# data
lift_path = Path(__file__).parent.parent.parent / "wyvern/data/sources/lift_dists"
lift_data = np.genfromtxt(lift_path / "Full_cruise_L.csv", delimiter=",", skip_header=1)
# normalize lift data
T = np.trapz(lift_data[:, 1], lift_data[:, 0])
lift_data[:, 1] = W0 * lift_data[:, 1] / T


def ell(y: float):
    # real lift distr
    return np.interp(y, lift_data[:, 0], lift_data[:, 1]) * n


rib_force = rib_loading(ell, y)

# Plotting
# do_3d_plots(structure)
rib_loading_plot(structure, rib_force, ell, n)
plt.savefig("rib_loads.pdf", bbox_inches="tight")

plt.show()
