from io import StringIO
from typing import Callable

import numpy as np
import numpy.typing as npt
from matplotlib import pyplot as plt
from scipy.integrate import quad


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


def spar_height(
    rib_y: npt.NDArray[np.floating],
    rib_c: npt.NDArray[np.floating],
    rib_xle: npt.NDArray[np.floating],
    spar_x: npt.NDArray[np.floating],
    sections: list[str],
) -> tuple[npt.NDArray[np.floating], npt.NDArray[np.floating]]:
    """
    Calculate the height of the spar at each rib.
    """
    num_ribs = len(rib_y)

    spar_tops = np.zeros(num_ribs)
    spar_bots = np.zeros(num_ribs)

    spar_points = spar_x - rib_xle

    ax = plt.figure().add_subplot(projection="3d")
    plt.tight_layout()

    for i in range(num_ribs):
        # read points from section file
        scale_fac = rib_c[i]
        section_coords = np.loadtxt(StringIO(sections[i])) * scale_fac

        section_x = section_coords[:, 0]
        section_y = section_coords[:, 1]

        # find breakpoint for top and bottom of section
        midpt = np.where(section_x == np.min(section_x))[0][0]

        x_top = section_x[: midpt + 1]
        y_top = section_y[: midpt + 1]
        x_bot = section_x[midpt:]
        y_bot = section_y[midpt:]

        # reverse top coordinates
        x_top = np.flip(x_top)
        y_top = np.flip(y_top)

        # interpolate to find y-coordinates of spar intersection
        spar_tops[i] = np.interp(spar_points[i], x_top, y_top)
        spar_bots[i] = np.interp(spar_points[i], x_bot, y_bot)

        ax.plot(x_top + rib_xle[i], rib_y[i] * np.ones_like(y_top), y_top, "r-")
        ax.plot(x_bot + rib_xle[i], rib_y[i] * np.ones_like(y_bot), y_bot, "b-")
        ax.plot(
            [spar_x[i], spar_x[i]],
            [rib_y[i], rib_y[i]],
            [spar_tops[i], spar_bots[i]],
            "g-",
        )
    ax.plot(spar_x, rib_y, spar_tops, "g-")
    ax.plot(spar_x, rib_y, spar_bots, "g-")

    ax.axis("equal")
    plt.subplots_adjust(left=-0.6, right=1.6, top=1.6, bottom=-0.6)
    ax.set_axis_off()
    return (spar_tops, spar_bots)
