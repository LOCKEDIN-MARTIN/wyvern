import numpy as np
import numpy.typing as npt
from matplotlib import pyplot as plt

from wyvern.analysis.structures.abstractions import Structure
from wyvern.analysis.structures.rib_calcs import get_section_coords


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
                linewidth=0.5,
            )
            ax.plot(
                airfoil.x_bot + rib_xle[j],
                rib_y[j] * np.ones_like(airfoil.y_bot),
                airfoil.y_bot,
                "k-",
                linewidth=0.5,
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


def do_3d_plots(
    structure: Structure,
):
    """
    I threw everything into this one function to free up the main script.
    """

    num_ribs = len(structure.rib)

    rib_spar_structure_plot(
        [structure.spars[0].ztop, structure.spars[1].ztop],
        [structure.spars[0].zbot, structure.spars[1].zbot],
        structure.rib.y,
        structure.rib.c,
        structure.rib.xle,
        [structure.spars[0].x, structure.spars[1].x],
        structure.rib.twist,
        structure.rib.sections,
    )

    with open("rib_spar_layout.txt", "w") as f:
        f.write("y\t x1\t z1_top\t z1_bot\t h1\tx2\t z2_top\t z2_bot\t h2\t\n")
        for i in range(num_ribs):
            f.write(
                f"{structure.rib.y[i]*1000:.2f}\t {structure.spars[0].x[i]*1000:.2f}\t {structure.spars[0].ztop[i]*1000:.2f}\t {structure.spars[0].zbot[i]*1000:.2f}\t {1000*(structure.spars[0].ztop[i] - structure.spars[0].zbot[i]):.1f} \t"
                f"{structure.spars[1].x[i]*1000:.2f}\t {structure.spars[1].ztop[i]*1000:.2f}\t {structure.spars[1].zbot[i]*1000:.2f}\t {1000*(structure.spars[1].ztop[i] - structure.spars[1].zbot[i]):.1f}\n"
            )

    plt.savefig("3d_structure.pdf", bbox_inches="tight")

    # switch to 2D view
    plt.gca().view_init(elev=0, azim=0)
    plt.subplots_adjust(left=-0.6, right=1.6, top=1.6, bottom=-0.6)
    plt.savefig("2d_structure.pdf", bbox_inches="tight")

    # side shot
    plt.gca().view_init(elev=0, azim=90)
    plt.savefig("side_structure.png", dpi=300)
