import numpy as np
from pandas import DataFrame

from wyvern.analysis.parameters import WingSizingParameters
from wyvern.data import (
    TURN_RADIUS,
)
from wyvern.utils.constants import RHO, G


def generate_flight_regimes(params: WingSizingParameters) -> DataFrame:
    """
    Generate flight regimes for the aircraft.

    Data frame of load factor, dyn. pressure and speed

    Regimes:
    - Stall
    - Cruise
    - Turn
    - Takeoff

    """

    # Compute load factor in turn
    n = np.sqrt((params.turn_speed**2 / (G * TURN_RADIUS)) ** 2 + 1)

    # the rest follows

    takeoff_speed = params.stall_speed * 1.05

    df = DataFrame(
        {
            "load_factor": [1, n, 1, 1],
            "dynamic_pressure": [
                0.5 * RHO * params.stall_speed**2,
                0.5 * RHO * params.turn_speed**2,
                0.5 * RHO * params.cruise_speed**2,
                0.5 * RHO * takeoff_speed**2,
            ],
            "speed": [
                params.stall_speed,
                params.turn_speed,
                params.cruise_speed,
                takeoff_speed,
            ],
        },
        index=["Stall", "Turn", "Cruise", "Takeoff"],
    )
    return df
