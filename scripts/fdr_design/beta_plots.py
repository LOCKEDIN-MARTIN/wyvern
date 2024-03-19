from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import rcParams

rcParams["text.usetex"] = True
# use computer modern serif font for all text
rcParams["font.family"] = "serif"


path_to_data = Path(__file__).parent.parent.parent / "wyvern/data/sources/beta_dists"

cl_beta_data = np.genfromtxt(path_to_data / "ClBeta.csv", delimiter=",", skip_header=1)
cn_beta_data = np.genfromtxt(path_to_data / "CnBeta.csv", delimiter=",", skip_header=1)

fig, axs = plt.subplots(1, 2, figsize=(8, 3), tight_layout=True)

axs[0].plot(cl_beta_data[:, 0], cl_beta_data[:, 1], "k")

axs[1].plot(cn_beta_data[:, 0], cn_beta_data[:, 1], "k")

axs[0].set_xlabel(r"$\beta$ (deg)")
axs[0].set_ylabel(r"$C_\ell$")
axs[0].set_title(r"$C_\ell$ vs $\beta$", fontsize=10)
axs[0].grid(linewidth=0.5, alpha=0.5)

axs[1].set_xlabel(r"$\beta$ (deg)")
axs[1].set_ylabel(r"$C_n$")
axs[1].set_title(r"$C_n$ vs $\beta$", fontsize=10)
axs[1].grid(linewidth=0.5, alpha=0.5)

# move spines of both axes
for ax in axs:
    ax.spines["left"].set_position("zero")
    ax.spines["right"].set_color("none")

    ax.set_xlim(0, 5)

    x_labels = ax.get_xticklabels()
    for label in x_labels:
        label.set_ha("right")

    y_labels = ax.get_yticklabels()
    for label in y_labels:
        label.set_ha("right")

axs[0].spines["top"].set_position("zero")
axs[0].spines["bottom"].set_color("none")
axs[0].tick_params(top=True, labeltop=True, bottom=False, labelbottom=False)

axs[1].spines["bottom"].set_position("zero")
axs[1].spines["top"].set_color("none")


plt.savefig("lateral_static_stab.pdf", bbox_inches="tight")

plt.show()
