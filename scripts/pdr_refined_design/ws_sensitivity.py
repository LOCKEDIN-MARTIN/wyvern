import numpy as np
from matplotlib import pyplot as plt

from wyvern.analysis.sensitivity import finite_diff_sensitivity
from wyvern.performance.models import QuadraticLDModel
from wyvern.utils.constants import G

ld_model = QuadraticLDModel(c_d0=0.0320, e_inviscid=0.95, K=0.45, aspect_ratio=5.106)
wing_loading_kgm2 = 2.874
wing_loading_Nm2 = wing_loading_kgm2 * G


def determine_sensitivity(w_s: float):
    return finite_diff_sensitivity(ld_model.v_ldmax, (w_s,), "wing_loading_Nm2")


w_s_range_kg = np.linspace(1.2, 4, 100)
sensitivities = np.array(list(map(determine_sensitivity, w_s_range_kg * G)))
v_ldmax_vals = np.array(list(map(ld_model.v_ldmax, w_s_range_kg * G)))


plt.subplot(2, 1, 1)
plt.plot(w_s_range_kg, v_ldmax_vals)
plt.xlabel("Wing loading (kg/m^2)")
plt.ylabel("V_LDmax")

plt.subplot(2, 1, 2)
plt.plot(w_s_range_kg, sensitivities)
plt.xlabel("Wing loading (kg/m^2)")
plt.ylabel("d(V_LDmax)/d(wing_loading)")

plt.show()
