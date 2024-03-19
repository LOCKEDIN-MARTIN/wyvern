from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import rcParams

clmax_arr = np.loadtxt("clmax.txt")

y_stations = clmax_arr[:, 0]
re_stations = clmax_arr[:, 1]
clmax = clmax_arr[:, 2]
alphastall = clmax_arr[:, 3]


# load reference data from XFLR5
ref_data = np.loadtxt(
    Path(__file__).parent.parent.parent / "wyvern/data/sources/stall_CLdist.csv",
    delimiter=",",
    skiprows=1,
    usecols=(0, 1),
)

y_xflr = ref_data[:, 0]
cl_xflr = ref_data[:, 1]

# filter only y points which are positive
cl_xflr = cl_xflr[y_xflr >= 0]
y_xflr = y_xflr[y_xflr >= 0]


rcParams["text.usetex"] = True
# use computer modern serif font for all text
rcParams["font.family"] = "serif"


plt.figure(figsize=(8, 4))
plt.plot(
    y_stations * 1000,
    clmax,
    color="cornflowerblue",
    marker="o",
    label="XFOIL Sectional $C_{\ell \mathrm{max}}$, $n_{\mathrm{crit}}=4$, $x_{TR} = 0.1$",
)
plt.plot(
    y_xflr * 1000,
    cl_xflr,
    color="red",
    label="XFLR5 $C_\ell$ Distribution (Inviscid VLM1)",
)
plt.grid(linewidth=0.5, alpha=0.5)
plt.yticks(np.arange(0.3, 1.5, 0.15))
plt.xlabel("Span Position (mm)")
plt.ylabel("$C_\ell$")
plt.axvline(
    x=780,
    color="green",
    linestyle="--",
    label=r"Onset of Stall, $y\approx780$ mm",
    linewidth=1,
)
plt.title("Stall Performance, $v=7$ m/s", fontsize=10)
# data annotations
for i, txt in enumerate(re_stations):
    plt.annotate(
        f"{clmax[i]:.3f}",
        (y_stations[i] * 1000, clmax[i]),
        textcoords="offset points",
        xytext=(0, 10),
        ha="center",
    )
plt.legend(loc="lower left")
plt.savefig("clmax.pdf", bbox_inches="tight")

plt.show()
