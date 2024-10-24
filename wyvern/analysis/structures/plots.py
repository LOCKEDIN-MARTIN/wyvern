from typing import Callable

import numpy as np
import numpy.typing as npt
from matplotlib import pyplot as plt
from matplotlib import rcParams

from wyvern.analysis.structures.abstractions import SparPoints, Structure
from wyvern.analysis.structures.rib_calcs import RibFLoads, get_section_coords
from wyvern.analysis.structures.spar_calcs import BeamDerivatives


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
        ax.plot(spar_x, rib_y * 1000, spar_tops, color=f"C{i}")
        ax.plot(spar_x, rib_y * 1000, spar_bots, color=f"C{i}")

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
        structure.rib.y * 1000,
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
    axs[0].plot(
        rib_y * 1000, structure.spars[0].x, color="forestgreen", label="Main Spar"
    )
    axs[0].plot(
        rib_y * 1000, structure.spars[1].x, color="darkseagreen", label="Secondary Spar"
    )
    axs[0].invert_yaxis()

    ax1_twin = axs[1].twinx()
    ax1_twin.bar(
        rib_y * 1000, rib_force, width=0.05, color="C1", alpha=0.8, edgecolor="k"
    )
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


def spar_plots(
    bd1: BeamDerivatives,
    bd2: BeamDerivatives,
    spar_1: SparPoints,
    spar_2: SparPoints,
    y: npt.NDArray[np.floating],
    b: float,
):
    rupture_strength = 19e6
    shear_strength = 1.10e6

    # Plotting
    rcParams["text.usetex"] = True
    # use computer modern serif font for all text
    rcParams["font.family"] = "serif"

    fig, axs = plt.subplots(2, 2, figsize=(10, 6), tight_layout=True)

    # BMD/Bending Stress Plot
    axs[0, 1].plot(y * 1000, bd1.bending_moment, "k-")
    axs[0, 1].set_title("Spar Bending")
    axs[0, 1].set_xlabel("y (m)")
    axs[0, 1].set_ylabel("Bending Moment (Nm)")
    axs[0, 1].set_ylim(0, max(bd1.bending_moment) * 1.1)
    axs012 = axs[0, 1].twinx()
    axs012.plot(y * 1000, bd1.bending_stress / 1e6, "r-", label="_Main Spar")
    axs012.plot(y * 1000, bd2.bending_stress / 1e6, "r--", label="_Secondary Spar")
    axs012.axhline(
        rupture_strength / 1e6 / 2,
        color="r",
        linestyle=":",
        label="$\sigma_{\mathrm{rupture}}$ (SF$=2$)",
    )
    axs012.set_ylabel("Bending Stress (MPa)", color="r")
    axs012.tick_params(axis="y", colors="r")
    axs012.set_ylim(0, max(bd1.bending_stress) / 1e6 * 1.1)
    axs012.set_yticks(
        sorted(axs012.get_yticks().tolist() + [rupture_strength / 1e6 / 2])
    )

    axs012.legend()

    # SFD/Shear Stress Plot
    axs[0, 0].plot(y * 1000, bd1.shear_force, "k-")
    axs[0, 0].set_title("Spar Shear")
    axs[0, 0].set_xlabel("y (mm)")
    axs[0, 0].set_ylabel("Shear Force (N)")
    axs[0, 0].set_ylim(0, max(bd1.shear_force) * 1.1)
    axs002 = axs[0, 0].twinx()
    axs002.plot(y * 1000, bd1.shear_stress / 1e6, "r-", label="_Main Spar")
    axs002.plot(y * 1000, bd2.shear_stress / 1e6, "r--", label="_Secondary Spar")
    axs002.axhline(
        shear_strength / 1e6 / 2,
        color="r",
        linestyle=":",
        label="$\sigma_{\mathrm{shear}}$ (SF$=2$)",
    )
    axs002.set_ylabel("Shear Stress (MPa)", color="r")
    axs002.tick_params(axis="y", colors="r")
    axs002.set_ylim(0, shear_strength / 2e6 * 1.1)
    axs002.set_yticks(sorted(axs002.get_yticks().tolist() + [shear_strength / 1e6 / 2]))
    axs002.legend()

    # Spar Profiles
    axs[1, 0].plot(spar_1.y * 1e3, spar_1.ztop * 1e3, "r-", label="_Main Spar")
    axs[1, 0].plot(spar_1.y * 1e3, spar_1.zbot * 1e3, "r-", label="_")
    axs[1, 0].plot(spar_2.y * 1e3, spar_2.ztop * 1e3, "r--", label="_Secondary Spar")
    axs[1, 0].plot(spar_2.y * 1e3, spar_2.zbot * 1e3, "r--", label="_")
    axs[1, 0].set_title("Spar Profile (exaggerated)")
    axs[1, 0].set_xlabel("y (mm)")
    axs[1, 0].set_ylabel("z (mm)")

    # deflections
    (h11,) = axs[1, 1].plot(y * 1000, bd1.deflection * 1000, "r-", label="_Main Spar")
    (h22,) = axs[1, 1].plot(
        y * 1000, bd2.deflection * 1000, "r--", label="_Secondary Spar"
    )
    axs[1, 1].set_title("Deflection")
    axs[1, 1].set_title("Deflection")
    axs[1, 1].set_xlabel("y (mm)")
    axs[1, 1].set_ylabel("Deflection (mm)")
    axs[1, 1].set_ylim(0, max(bd2.deflection) * 1000 * 1.1)
    axs[1, 1].secondary_yaxis(
        "right", functions=(lambda y: y / 1e3 / b * 100, lambda y: y / 1e3 / b * 100)
    ).set_ylabel("Deflection (\% Span)")

    for ax in axs.flat:
        ax.grid(linewidth=0.5, alpha=0.5)
        ax.set_xlim(-b / 2 * 1000, b / 2 * 1000)

    fig.legend(
        handles=[h11, h22],
        labels=["Main Spar", "Secondary Spar"],
        loc="center",
        bbox_to_anchor=(0.5, 0.5),
    )


def rib_failure_plot(
    rib_f_loads: RibFLoads,
    rib_loading: npt.NDArray[np.floating],
    y: npt.NDArray[np.floating],
):
    crushing_strength = 1e6
    shear_strength = 1.10e6

    # Plotting
    rcParams["text.usetex"] = True
    # use computer modern serif font for all text
    rcParams["font.family"] = "serif"

    fig, axs = plt.subplots(3, 1, figsize=(6, 6), tight_layout=True, sharex=True)

    # Crushing
    axs[0].bar(
        y * 1000,
        rib_f_loads.crushing / 1e6,
        width=50,
        color="C0",
        alpha=0.8,
        edgecolor="k",
    )
    axs[0].set_title("Rib Crushing", fontsize=10)
    axs[0].set_ylabel("Crushing Stress (MPa)")
    axs[0].axhline(
        crushing_strength / 1e6 / 2,
        color="r",
        linestyle=":",
        label="$\sigma_{\mathrm{crush}}$ (SF$=2$)",
    )
    axs[0].legend()
    axs[0].grid(linewidth=0.5, alpha=0.5)
    axs[0].set_ylim(0, 0.6)

    # Shear
    axs[1].bar(
        y * 1000,
        rib_f_loads.shear / 1e6,
        width=50,
        color="C0",
        alpha=0.8,
        edgecolor="k",
        label="_",
    )
    axs[1].set_title("Rib Shear, $h_{\mathrm{min}} = 7$ mm", fontsize=10)
    axs[1].set_ylabel("Shear Stress (MPa)")
    axs[1].axhline(
        shear_strength / 1e6 / 2,
        color="r",
        linestyle=":",
        label="$\sigma_{\mathrm{shear}}$ (SF$=2$)",
    )
    axs[1].legend()
    axs[1].grid(linewidth=0.5, alpha=0.5)
    axs[1].set_ylim(0, 0.6)

    # Buckling
    axs[2].bar(
        y * 1000,
        rib_f_loads.buckling_1 / 2,
        width=50,
        color="C0",
        alpha=0.8,
        edgecolor="k",
        label="At Main Spar",
        zorder=1,
    )
    axs[2].bar(
        y * 1000,
        rib_f_loads.buckling_2 / 2,
        width=50,
        color="C1",
        alpha=0.8,
        edgecolor="k",
        label="At Secondary Spar",
        zorder=0,
    )
    axs[2].plot(y * 1000, rib_loading / 2, "r--", marker="o", label="Actual Loading")
    axs[2].set_title("Rib Buckling, $c_{\mathrm{min}} = 50$ mm, SF = 2", fontsize=10)
    axs[2].set_ylabel("Critical Load / 2 (N)")
    axs[2].grid(linewidth=0.5, alpha=0.5)
    axs[2].legend(ncol=3)
    # scale as log
    axs[2].set_yscale("log")
    axs[2].set_ylim(1e-1, 1e3)

    axs[2].set_xlabel("y (mm)")
    axs[2].set_xticks(y * 1000)
