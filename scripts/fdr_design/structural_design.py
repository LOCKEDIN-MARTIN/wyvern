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
from wyvern.analysis.structures.plots import (
    do_3d_plots,
    rib_failure_plot,
    rib_loading_plot,
    spar_plots,
)
from wyvern.analysis.structures.rib_calcs import rib_failure, rib_loading
from wyvern.analysis.structures.spar_calcs import beam_derivatives
from wyvern.utils.constants import G
from wyvern.utils.geom_utils import mirror_verts

# aircraft parameters
M0 = 1.63  # kg
W0 = M0 * G  # N
b = 1.7  # m; span
n = 3.59  # load factor
spar_width = 1 / 8 * 25.4e-3  # m; spar width

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
rib_min_t = 7e-3  # m; minimum rib thickness point
rib_min_c = 100e-3  # m; minimum contiguous length

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

# rib_loading_plot(structure, rib_force, ell, n)
# plt.savefig("rib_loads.pdf", bbox_inches="tight")

y_loading = np.linspace(-b / 2, b / 2, 200)
h_smooth_1 = np.interp(y_loading, y, structure.spars[0].h)
h_smooth_2 = np.interp(y_loading, y, structure.spars[1].h)

E = 2.55e9

bd = [
    beam_derivatives(ell, y_loading, spar_width, h_smooth_1, E),
    beam_derivatives(ell, y_loading, spar_width, h_smooth_2, E),
]

spar_plots(bd[0], bd[1], structure.spars[0], structure.spars[1], y_loading, b)
plt.savefig("spar_loads.pdf", bbox_inches="tight")

rib_f_loads = rib_failure(structure, rib_force, rib_min_t, rib_min_t, spar_width * 2)
rib_failure_plot(rib_f_loads, rib_force, structure.rib.y)
plt.savefig("rib_failure.pdf", bbox_inches="tight")
# plt.show()
