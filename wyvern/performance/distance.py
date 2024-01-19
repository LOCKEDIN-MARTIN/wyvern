import numpy as np

from wyvern.data import (
    NUMBER_OF_STRAIGHTS,
    NUMBER_OF_TURNS,
    STRAIGHT_SEGMENT_LENGTH,
    TURN_RADIUS,
)


def course_lengths() -> tuple[float, float]:
    """Length of course.

    Straights, Turns.

    Returns
    -------
    tuple[float, float]
        Length of course in m.
    """
    return (
        STRAIGHT_SEGMENT_LENGTH * NUMBER_OF_STRAIGHTS,
        np.pi * TURN_RADIUS * NUMBER_OF_TURNS,
    )


def flight_times(cruise_speed: float, turn_speed: float) -> tuple[float, float]:
    """Flight times in each phase.

    Parameters
    ----------
    cruise_speed : float
        Cruise speed in m/s
    turn_speed : float
        Turn speed in m/s.


    Returns
    -------
    tuple[float, float]
        Flight times in each phase in seconds.
    """
    return (
        STRAIGHT_SEGMENT_LENGTH * NUMBER_OF_STRAIGHTS / cruise_speed,
        np.pi * TURN_RADIUS * NUMBER_OF_TURNS / turn_speed,
    )
