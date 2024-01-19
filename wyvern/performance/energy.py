from wyvern.data import TURN_RADIUS
import numpy as np
from wyvern.performance.distance import course_lengths


def energy_consumption(
    mass: float, cruise_speed: float, turn_speed: float, lift_to_drag_ratio: float
) -> float:
    """
    "Raw" energy consumption over the course. Divide by propulsive efficiency to get effective battery energy consumption.

    Parameters
    ----------
    mass : float
        Mass of aircraft in g.
    cruise_speed : float
        Cruise speed in m/s
    turn_speed : float
        Turn speed in m/s.
    lift_to_drag_ratio : float
        Lift to drag ratio.

    Returns
    -------
    float
        Energy consumption in J.
    """
    g_0 = 9.80665

    # Compute load factor in turn
    n = np.sqrt((turn_speed**2 / (g_0 * TURN_RADIUS)) ** 2 + 1)

    weight = mass / 1000 * g_0  # N

    (l_s, l_t) = course_lengths()

    return weight / lift_to_drag_ratio * (l_s + n * l_t)
