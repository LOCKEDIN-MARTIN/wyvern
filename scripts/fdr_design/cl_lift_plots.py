from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import rcParams

rcParams["text.usetex"] = True
# use computer modern serif font for all text
rcParams["font.family"] = "serif"


path_to_data = Path(__file__).parent.parent.parent / "wyvern/data/sources/lift_dists"

configurations = ["Full", "Empty"]
conditions = ["stall", "cruise", "takeoff"]
colours = ["k", "C0", "r"]
linestyles = ["-.", "-", "--"]

for config in configurations:

    # left plot for lift distribution, right plot for CL
    fig, axs = plt.subplots(2, 1, figsize=(5, 5), sharex=True, tight_layout=True)

    axs[0].set_ylabel("$\ell(y)$ (N/m)")
    axs[0].set_title("Lift Distribution (n = 1)", fontsize=10)
    axs[0].grid(linewidth=0.5, alpha=0.5)

    axs[1].set_ylabel("$C_L$")
    axs[1].set_xlabel("$y$ (mm)")
    axs[1].set_title("$C_L$ Distribution", fontsize=10)
    axs[1].grid(linewidth=0.5, alpha=0.5)

    # plot refernece elliptical distr

    b = 1.7
    y = np.linspace(-b / 2, b / 2, 200)

    W = 1.63 * 9.80665 if config == "Full" else 1.185 * 9.80665

    l_ellip = 4 * W / (b * np.pi) * np.sqrt(1 - (2 * y / b) ** 2)
    axs[0].fill_between(
        y * 1e3,
        l_ellip,
        color="gold",
        alpha=0.3,
        label="(Elliptical)",
    )
    axs[0].plot(y * 1e3, l_ellip, color="orange", linewidth=1, label="_")

    for i, cond in enumerate(conditions):
        cl_data = np.genfromtxt(
            path_to_data / f"{config}_{cond}_CL.csv", delimiter=",", skip_header=1
        )
        lift_data = np.genfromtxt(
            path_to_data / f"{config}_{cond}_L.csv", delimiter=",", skip_header=1
        )

        # normalize lift data
        T = np.trapz(lift_data[:, 1], lift_data[:, 0])
        lift_data[:, 1] = W * lift_data[:, 1] / T

        axs[0].plot(
            lift_data[:, 0] * 1e3,
            lift_data[:, 1],
            color=colours[i],
            label=cond.title(),
            linewidth=1,
            linestyle=linestyles[i],
        )
        axs[1].plot(
            cl_data[:, 0] * 1e3,
            cl_data[:, 1],
            color=colours[i],
            label=cond.title(),
            linewidth=1,
            linestyle=linestyles[i],
        )

    box = axs[0].get_position()
    axs[0].legend(
        fontsize=8,
        loc="upper center",
        bbox_to_anchor=(0.50, -0.1),
        frameon=False,
        ncol=4,
    )

    axs[1].set_yticks([0, 0.3, 0.6, 0.9, 1.2])
    axs[1].set_ylim(0, 1.2)

    axs[0].set_yticks([0, 3, 6, 9, 12, 15])
    axs[0].set_ylim(0, 15)
    axs[0].set_xticks(
        [
            -850,
            -630,
            -420,
            -185,
            0,
            185,
            420,
            630,
            850,
        ]
    )

    for ax in axs:
        # turn off right and top spines
        ax.spines["right"].set_color("none")
        ax.spines["top"].set_color("none")

    plt.savefig(f"{config}_lift_dist.pdf", bbox_inches="tight")
