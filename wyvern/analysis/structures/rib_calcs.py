from dataclasses import dataclass
from io import StringIO
from typing import Callable

import numpy as np
import numpy.typing as npt
from scipy.integrate import quad


@dataclass
class AirfoilPoints:
    # all arrays should be monotonically increasing
    x_top: npt.NDArray[np.floating]
    y_top: npt.NDArray[np.floating]
    x_bot: npt.NDArray[np.floating]
    y_bot: npt.NDArray[np.floating]


def rib_loading(lift_distribution: Callable[[float], float], rib_y: npt.NDArray):
    """
    Calculate the lift loading on each rib.
    """
    num_ribs = len(rib_y)

    rib_force = np.zeros(num_ribs)

    for i in range(num_ribs):
        if i == 0:
            bound_l = rib_y[i]
        else:
            bound_l = (rib_y[i - 1] + rib_y[i]) / 2

        if i == num_ribs - 1:
            bound_r = rib_y[i]
        else:
            bound_r = (rib_y[i] + rib_y[i + 1]) / 2

        rib_force[i] = quad(lift_distribution, bound_l, bound_r)[0]

    return rib_force


def get_section_coords(
    section: str, scale_fac: float, twist: float = 0, twist_xc: float = 0.5
) -> AirfoilPoints:
    """
    Get the coordinates of a section.
    """
    section_coords = section * scale_fac

    section_x = section_coords[:, 0]
    section_y = section_coords[:, 1]

    # find breakpoint for top and bottom of section
    midpt = np.where(section_x == np.min(section_x))[0][0]

    # twist section
    section_y = section_y * np.cos(twist * np.pi / 180) + (
        section_x - twist_xc * scale_fac
    ) * np.sin(twist * np.pi / 180)
    section_x = (
        (section_x - twist_xc * scale_fac) * np.cos(twist * np.pi / 180)
        - (section_y) * np.sin(twist * np.pi / 180)
        + twist_xc * scale_fac
    )

    x_top = section_x[: midpt + 1]
    y_top = section_y[: midpt + 1]
    x_bot = section_x[midpt:]
    y_bot = section_y[midpt:]

    # reverse top coordinates
    x_top = np.flip(x_top)
    y_top = np.flip(y_top)

    return AirfoilPoints(x_top, y_top, x_bot, y_bot)


def spar_height(
    rib_y: npt.NDArray[np.floating],
    rib_c: npt.NDArray[np.floating],
    rib_xle: npt.NDArray[np.floating],
    spar_x: npt.NDArray[np.floating],
    twist: npt.NDArray[np.floating],
    sections: list[str],
) -> tuple[npt.NDArray[np.floating], npt.NDArray[np.floating]]:
    """
    Calculate the height of the spar at each rib.
    """
    num_ribs = len(rib_y)

    spar_tops = np.zeros(num_ribs)
    spar_bots = np.zeros(num_ribs)

    spar_points = spar_x - rib_xle

    for i in range(num_ribs):
        # read points from section file
        scale_fac = rib_c[i]

        airfoil = get_section_coords(sections[i], scale_fac, twist[i])

        # interpolate to find y-coordinates of spar intersection
        spar_tops[i] = np.interp(spar_points[i], airfoil.x_top, airfoil.y_top)
        spar_bots[i] = np.interp(spar_points[i], airfoil.x_bot, airfoil.y_bot)

    return (spar_tops, spar_bots)
