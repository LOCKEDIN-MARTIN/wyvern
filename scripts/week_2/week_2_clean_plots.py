import matplotlib.pyplot as plt

from wyvern.data import PLANFORM_CONFIGS
from wyvern.layout import planform_viz_simple

# define planform parameters
plt.style.use("dark_background")
planform_viz_simple(PLANFORM_CONFIGS["NF-844-D"])
