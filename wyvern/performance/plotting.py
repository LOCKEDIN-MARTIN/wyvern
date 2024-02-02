import numpy as np
from matplotlib import pyplot as plt

from wyvern.performance.models import QuadraticLDModel
from wyvern.performance.thrust_power import power_required, thrust_required


def plot_drag_polar(ld_model: QuadraticLDModel, cL_lims: tuple[float] = (-0.2, 1.2)):
    """
    Plot the drag polar for a given lift and drag model.

    Includes line of tangency and maximum L/D point.
    """
    cL_range = np.linspace(*cL_lims, 100)
    cD_range = ld_model.c_D(cL_range)

    max_pt = (ld_model.c_d_ldmax, ld_model.c_l_ldmax)

    plt.plot(cD_range, cL_range)

    # plot line of tangency
    xcd = np.linspace(0, 0.7 * max(cD_range), 100)
    y = xcd * max_pt[1] / max_pt[0]
    plt.plot(xcd, y)

    # mark maximum L/D point
    plt.scatter(*max_pt, color="red", label=f"Max L/D = {ld_model.l_d_max:.2f}")

    plt.xlabel("C_D")
    plt.ylabel("C_L")
    plt.grid()
    plt.title("Drag polar")
    plt.legend()
    plt.show()

    return None


def power_plot(ld_model: QuadraticLDModel, wing_loading_Nm2: float):
    """
    Plot power required for a given wing loading.
    """
    speed_range = np.linspace(4, 15, 100)
    power_range = np.array(
        [power_required(ld_model, s, wing_loading_Nm2) for s in speed_range]
    )

    plt.plot(speed_range, power_range)
    plt.xlabel("Speed (m/s)")
    plt.ylabel("Power required (W)")
    plt.grid()
    plt.title("Power required")
    plt.show()

    return None
