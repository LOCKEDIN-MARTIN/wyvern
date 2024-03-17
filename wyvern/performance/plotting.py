import numpy as np
from matplotlib import pyplot as plt

from wyvern.data.propellers import PropellerCurve
from wyvern.performance.models import QuadraticLDModel
from wyvern.performance.thrust_power import power_required, thrust_required


def plot_drag_polar(ld_model: QuadraticLDModel, cL_lims: tuple[float] = (-0.2, 1.2)):
    """
    Plot the drag polar for a given lift and drag model.

    Includes line of tangency and maximum L/D point.

    saving or showing the plot is up to the user.
    """
    cL_range = np.linspace(*cL_lims, 100)
    cD_range = ld_model.c_D(cL_range)

    max_pt = (ld_model.c_d_ldmax, ld_model.c_l_ldmax)

    plt.plot(cD_range, cL_range, "-k")

    # plot line of tangency
    xcd = np.linspace(0, 0.7 * max(cD_range), 100)
    y = xcd * max_pt[1] / max_pt[0]
    plt.plot(xcd, y, linestyle="--", color="r", linewidth=1)

    # mark maximum L/D point
    plt.scatter(*max_pt, color="r", label=f"Max L/D = {ld_model.l_d_max:.2f}")

    plt.xlabel("$C_D$")
    plt.ylabel("$C_L$")
    plt.yticks(np.arange(-0.2, 1.2, 0.2))
    plt.grid(linewidth=0.5, alpha=0.5)
    plt.title("Drag polar", fontsize=10)
    plt.legend()


def thrust_plot(
    ld_model: QuadraticLDModel,
    wing_loading_Nm2: float,
    wing_area_m2: float,
    propeller_model: PropellerCurve,
):
    """
    Plot thrust required vs thrust available for a given wing loading.
    """
    speed_range = np.linspace(4, 20, 100)
    speed_range_ex = np.linspace(0, 20, 100)
    thrust_range = np.array(
        [
            thrust_required(ld_model, s, wing_loading_Nm2, wing_area_m2)
            for s in speed_range
        ]
    )

    # interpolant for thrust available
    thrust_available = np.interp(speed_range_ex, propeller_model.v, propeller_model.T)

    plt.plot(speed_range, thrust_range, "-k", label="$T_R$")
    plt.plot(speed_range_ex, thrust_available, "-r", label="$T_A$")
    plt.xlabel("Speed (m/s)")
    plt.ylabel("Thrust (N)")
    plt.xlim(0, 20)
    plt.grid(linewidth=0.5, alpha=0.5)
    plt.title("Thrust Performance")
    plt.legend(frameon=False)


def power_plot(
    ld_model: QuadraticLDModel,
    wing_loading_Nm2: float,
    wing_area_m2: float,
    propeller_model: PropellerCurve,
) -> tuple[float, float]:
    """
    Plot power required vs power available for a given wing loading.

    saving or showing the plot is up to the user.

    JANK: computes v of most excess power and no excess power
    """
    speed_range = np.linspace(4, 20, 100)
    power_range = np.array(
        [
            power_required(ld_model, s, wing_loading_Nm2, wing_area_m2)
            for s in speed_range
        ]
    )

    # interpolant for power available
    power_available = np.interp(speed_range, propeller_model.v, propeller_model.P)

    excess_power = power_available - power_range
    v_excess = speed_range[np.argmax(excess_power)]
    v_max = speed_range[np.argmin(np.abs(excess_power))]

    plt.plot(speed_range, power_range, "-k", label="$P_R$")
    plt.plot(speed_range, power_available, "-r", label="$P_A$")
    plt.xlabel("Speed (m/s)")
    plt.ylabel("Power (W)")
    plt.xlim(0, 20)
    plt.grid(linewidth=0.5, alpha=0.5)
    plt.title("Power Performance")
    plt.legend(frameon=False)

    return v_excess, v_max
