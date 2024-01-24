import numpy as np
from pandas import DataFrame

from wyvern.analysis.parameters import WingSizingParameters
from wyvern.data import (
    TURN_RADIUS,
)


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

    g_0 = 9.80665
    rho = 1.225  # kg/m^3

    # Compute load factor in turn
    n = np.sqrt((params.turn_speed**2 / (g_0 * TURN_RADIUS)) ** 2 + 1)

    # the rest follows

    takeoff_speed = params.stall_speed * 1.05

    df = DataFrame(
        {
            "load_factor": [1, n, 1, 1],
            "dynamic_pressure": [
                0.5 * rho * params.stall_speed**2,
                0.5 * rho * params.turn_speed**2,
                0.5 * rho * params.cruise_speed**2,
                0.5 * rho * takeoff_speed**2,
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
