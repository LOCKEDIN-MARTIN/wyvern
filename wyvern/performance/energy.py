import numpy as np

from wyvern.data import TURN_RADIUS
from wyvern.performance.aerodynamics import ld_at_speed
from wyvern.performance.distance import course_lengths
from wyvern.performance.models import QuadraticLDModel
from wyvern.utils.constants import RHO, G

turn_fudge = 1.25


def energy_consumption(
    mass: float,
    cruise_speed: float,
    turn_speed: float,
    aero_model: QuadraticLDModel,
    wing_area: float,
) -> tuple[float, float]:
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
    aero_model : QuadraticLDModel
        Quadratic lift-drag model.
    wing_area : float
        Wing area in m^2.

    Returns
    -------
    float
        Energy consumption in J (propulsive)
    """

    # Compute load factor in turn
    n = np.sqrt((turn_speed**2 / (G * TURN_RADIUS)) ** 2 + 1)

    weight = mass / 1000 * G  # N

    # compute l/d in cruise and turn
    ld_cruise = ld_at_speed(cruise_speed, weight, aero_model, wing_area)
    ld_turn = ld_at_speed(turn_speed, weight * n, aero_model, wing_area)

    (l_s, l_t) = course_lengths()

    e_cruise = weight * l_s / ld_cruise
    e_turn = weight * n * l_t / ld_turn * turn_fudge

    return e_cruise, e_turn
