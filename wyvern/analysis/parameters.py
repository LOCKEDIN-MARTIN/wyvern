from dataclasses import dataclass


@dataclass
class AssumedParameters:
    """
    Assumed parameters for the analysis
    """

    lift_to_drag_ratio: float
    cruise_speed: float
    turn_speed: float
    propulsive_efficiency: float
    configuration_bonus: float = 1.0
    short_takeoff: bool = False
    stability_distance: float = 0
