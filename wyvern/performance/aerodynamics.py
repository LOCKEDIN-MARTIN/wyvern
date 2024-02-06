import numpy as np

from wyvern.data import (
    TURN_RADIUS,
)
from wyvern.performance.models import QuadraticLDModel
from wyvern.utils.constants import RHO, G


def cl_required(flight_speed: float, lift_required: float, wing_area: float) -> float:
    """
    Required lift coefficient for a given flight speed and lift required.

    Parameters
    ----------
    flight_speed : float
        Flight speed in m/s
    lift_required : float
        Lift required in N

    Returns
    -------
    float
        Required lift coefficient.
    """
    return 2 * lift_required / (RHO * flight_speed**2 * wing_area)


def ld_at_speed(
    flight_speed: float,
    lift_required: float,
    aero_model: QuadraticLDModel,
    wing_area: float,
) -> float:
    """
    Lift to drag ratio at a given flight speed.
    """
    cl = cl_required(flight_speed, lift_required, wing_area)
    return cl / aero_model.c_D(cl)


def load_factor(turn_speed: float) -> float:
    """
    Load factor in a turn.
    """
    return np.sqrt((turn_speed**2 / (G * TURN_RADIUS)) ** 2 + 1)
