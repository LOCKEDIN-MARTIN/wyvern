import numpy as np
import numpy.typing as npt
from matplotlib import pyplot as plt

from wyvern.analysis.rib_analysis.calcs import get_section_coords


def rib_spar_structure_plot(
    spar_top: list[npt.NDArray[np.floating]],
    spar_bot: list[npt.NDArray[np.floating]],
    rib_y: npt.NDArray[np.floating],
    rib_c: npt.NDArray[np.floating],
    rib_xle: npt.NDArray[np.floating],
    spar_xs: list[npt.NDArray[np.floating]],
    twist: npt.NDArray[np.floating],
    sections: list[str],
):
    """
    Plot 3D views of spar and rib layout.
    """
    num_ribs = len(rib_y)
    ax = plt.gcf().add_subplot(projection="3d")
    plt.tight_layout()

    for i, (spar_x, spar_tops, spar_bots) in enumerate(
        zip(spar_xs, spar_top, spar_bot)
    ):

        for j in range(num_ribs):
            airfoil = get_section_coords(sections[j], rib_c[j], twist[j])

            # plot airfoil
            ax.plot(
                airfoil.x_top + rib_xle[j],
                rib_y[j] * np.ones_like(airfoil.y_top),
                airfoil.y_top,
                "k-",
            )
            ax.plot(
                airfoil.x_bot + rib_xle[j],
                rib_y[j] * np.ones_like(airfoil.y_bot),
                airfoil.y_bot,
                "k-",
            )
            # plot spar lines
            ax.plot(
                [spar_x[j], spar_x[j]],
                [rib_y[j], rib_y[j]],
                [spar_tops[j], spar_bots[j]],
                "g-",
            )
        ax.plot(spar_x, rib_y, spar_tops, color=f"C{i}")
        ax.plot(spar_x, rib_y, spar_bots, color=f"C{i}")

    ax.axis("equal")
    plt.subplots_adjust(left=-0.8, right=1.7, top=1.7, bottom=-0.7)
    ax.set_axis_off()
