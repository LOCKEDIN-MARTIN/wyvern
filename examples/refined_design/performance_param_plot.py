import numpy as np
from matplotlib import pyplot as plt

from wyvern.performance.models import QuadraticLDModel
from wyvern.performance.plotting import plot_drag_polar, power_plot

ld_model = QuadraticLDModel(c_d0=0.0318, e_inviscid=0.97, K=0.45, aspect_ratio=4.9)

plot_drag_polar(ld_model)

# plot L/D with CL, and L^1.5/D

cL_range = np.linspace(0, 1.2, 100)
cD_range = ld_model.c_D(cL_range)
ld = cL_range / cD_range
ld_15 = cL_range**1.5 / cD_range

plt.plot(cL_range, ld, label="CL/CD")
plt.plot(cL_range, ld_15, label="CL^1.5/CD")

plt.xlabel("C_L")
plt.ylabel("Dimensionless")

plt.grid()
plt.title("Performance parameters")
plt.legend()
plt.show()


power_plot(ld_model, 2.804 * 9.81)
