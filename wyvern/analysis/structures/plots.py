from typing import Callable

import numpy as np
import numpy.typing as npt
from matplotlib import pyplot as plt
from matplotlib import rcParams

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


def rib_loading_plot(
    structure: Structure,
    rib_force: npt.NDArray[np.floating],
    ell: Callable[[float], float],
    n: float,
):
    # latex plots
    rcParams["text.usetex"] = True
    # use computer modern serif font for all text
    rcParams["font.family"] = "serif"

    num_ribs = len(structure.rib)
    rib_y = structure.rib.y

    # Plots
    fig, axs = plt.subplots(2, 1, tight_layout=True, sharex=True, figsize=(6, 6))

    for i in range(num_ribs):
        axs[0].plot(
            [rib_y[i], rib_y[i]],
            [structure.rib.xle[i], structure.rib.xle[i] + structure.rib.c[i]],
            "k-",
        )
    axs[0].plot(rib_y, structure.spars[0].x, color="forestgreen", label="Main Spar")
    axs[0].plot(
        rib_y, structure.spars[1].x, color="darkseagreen", label="Secondary Spar"
    )
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
