from dataclasses import dataclass

import numpy as np
import numpy.typing as npt

from wyvern.analysis.structures.rib_calcs import spar_height
from wyvern.data.airfoils import BOEING_VERTOL, NACA0018
from wyvern.utils.geom_utils import mirror_verts


@dataclass
class RibControlPoints:
    """
    y: spanwise stations (mm)
    t: rib thickness (inches)
    c: chord (mm)
    xle: leading edge x-coordinate (mm)
    twist: twist angle (degrees downwards)
    """

    y: npt.NDArray[np.floating]
    c: npt.NDArray[np.floating]
    t: npt.NDArray[np.floating]
    xle: npt.NDArray[np.floating]
    twist: npt.NDArray[np.floating]

    def __post_init__(self):
        self.sections = [BOEING_VERTOL if y < 0.185 else NACA0018 for y in self.y]
        # mirror all control points and convert to meters
        self.y = mirror_verts(self.y) * 1e-3
        self.c = mirror_verts(self.c, negate=False) * 1e-3
        self.t = mirror_verts(self.t, negate=False) * 1e-3 * 25.4  # inches
        self.xle = mirror_verts(self.xle, negate=False) * 1e-3
        self.twist = mirror_verts(self.twist, negate=False)

    def __len__(self):
        return len(self.y)


@dataclass
class SparControlPoints:
    y: npt.NDArray[np.floating]
    x: npt.NDArray[np.floating]

    def __post_init__(self):
        # extrapolate to y=0 if needed
        if self.y[0] != 0:
            self.x = np.insert(
                self.x,
                0,
                self.x[0]
                + ((self.x[1]) - (self.x[0]))
                / (self.y[1] - self.y[0])
                * (0 - self.y[0]),
            )
            self.y = np.insert(self.y, 0, 0)

        # mirror all control points and convert to meters
        self.y = mirror_verts(self.y) * 1e-3
        self.x = mirror_verts(self.x, negate=False) * 1e-3


@dataclass
class StructurePoints:
    y: npt.NDArray[np.floating]
    rib_c: npt.NDArray[np.floating]
    rib_xle: npt.NDArray[np.floating]
    rib_sections: list
    twist: npt.NDArray[np.floating]

    spar_1_x: npt.NDArray[np.floating]
    spar_1_ztop: npt.NDArray[np.floating]
    spar_1_zbot: npt.NDArray[np.floating]
    spar_2_x: npt.NDArray[np.floating]
    spar_2_ztop: npt.NDArray[np.floating]
    spar_2_zbot: npt.NDArray[np.floating]

    @classmethod
    def from_structure(
        cls,
        y: npt.NDArray[np.floating],
        rib: RibControlPoints,
        spar_1: SparControlPoints,
        spar_2: SparControlPoints,
    ):
        # make structure from y stations and rib control points
        rib_c = np.interp(y, rib.y, rib.c)
        rib_xle = np.interp(y, rib.y, rib.xle)
        rib_sections = [BOEING_VERTOL if y < 0.185 else NACA0018 for y in y]
        twist = np.interp(y, rib.y, rib.twist)

        spar_1_x = np.interp(y, spar_1.y, spar_1.x)
        spar_2_x = np.interp(y, spar_2.y, spar_2.x)

        spar_1_ztop, spar_1_zbot = spar_height(
            y, rib_c, rib_xle, spar_1_x, twist, rib_sections
        )
        spar_2_ztop, spar_2_zbot = spar_height(
            y, rib_c, rib_xle, spar_2_x, twist, rib_sections
        )

        return cls(
            y,
            rib_c,
            rib_xle,
            rib_sections,
            twist,
            spar_1_x,
            spar_1_ztop,
            spar_1_zbot,
            spar_2_x,
            spar_2_ztop,
            spar_2_zbot,
        )
