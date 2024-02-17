import matplotlib.pyplot as plt

from wyvern.data import PLANFORM_CONFIGS
from wyvern.layout import planform_viz_simple
from wyvern.layout.planform import planform_span_stations, span_stations_to_tikz

# define planform parameters
# plt.style.use("dark_background")
planform_viz_simple(PLANFORM_CONFIGS["NF-844-D"])

plt.savefig("NF-844-D_planform.pdf", bbox_inches="tight")

with open("NF-844-D_span_stations.tex", "w") as f:
    f.write(span_stations_to_tikz(planform_span_stations(PLANFORM_CONFIGS["NF-844-D"])))
