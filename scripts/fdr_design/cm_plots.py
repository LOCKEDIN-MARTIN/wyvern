from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import rcParams

rcParams["text.usetex"] = True
# use computer modern serif font for all text
rcParams["font.family"] = "serif"


path_to_data = Path(__file__).parent.parent.parent / "wyvern/data/sources/cm_variation"

cm_alpha_data = np.genfromtxt(
    path_to_data / "Cm-alpha.csv", delimiter=",", skip_header=1
)
cma_np = cm_alpha_data[:, 1]
cma_cg = cm_alpha_data[:, 4]

cm_cl_data = np.genfromtxt(path_to_data / "Cm-CL.csv", delimiter=",", skip_header=1)

cml_np = cm_cl_data[:, 1]
cml_cg = cm_cl_data[:, 4]

fig, axs = plt.subplots(1, 2, figsize=(8, 3), sharey=True, tight_layout=True)

(h1,) = axs[0].plot(cm_alpha_data[:, 0], cma_cg, "k", label="CG = 0.380 m")
(h2,) = axs[0].plot(cm_alpha_data[:, 0], cma_np, "r", label="CP = NP = 0.400 m")

axs[1].plot(cm_cl_data[:, 0], cml_cg, "k", label="_CG = 0.380 m")
axs[1].plot(cm_cl_data[:, 0], cml_np, "r", label="_CP = NP = 0.400 m")

axs[0].set_xlabel(r"$\alpha$ (deg)")
axs[0].set_ylabel(r"$C_m$")
axs[0].set_title(r"$C_m$ vs $\alpha$", fontsize=10)
axs[0].grid(linewidth=0.5, alpha=0.5)

axs[1].set_xlabel(r"$C_L$")
axs[1].set_title(r"$C_m$ vs $C_L$", fontsize=10)
axs[1].grid(linewidth=0.5, alpha=0.5)

# move spines of both axes
for ax in axs:
    ax.spines["left"].set_position("zero")
    ax.spines["right"].set_color("none")
    ax.spines["bottom"].set_position("zero")
    ax.spines["top"].set_color("none")

    x_labels = ax.get_xticklabels()
    for label in x_labels:
        label.set_ha("right")
        label.set_rotation(30)

    y_labels = ax.get_yticklabels()
    for label in y_labels:
        label.set_ha("right")

axs[0].set_xlim(0, 17)

# place ax0 legend in between the two plots
fig.legend(
    [h1, h2],
    [h1._label, h2._label],
    loc="upper center",
    frameon=False,
    bbox_to_anchor=(0.47, 0.65),
    fontsize=8,
)
plt.savefig("cm_variation.pdf", bbox_inches="tight")

plt.show()
