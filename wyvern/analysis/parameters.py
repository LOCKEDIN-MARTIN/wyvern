import json
from dataclasses import asdict, dataclass


@dataclass
class SerializableParameters:
    """
    Base class for serializable parameters
    """

    @property
    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, d):
        return cls(**d)

    def to_json(self) -> str:
        return json.dumps(self.to_dict)

    @classmethod
    def from_json(cls, s: str):
        return cls.from_dict(json.loads(s))


@dataclass
class PayloadSizingParameters(SerializableParameters):
    """
    Parameters for payload sizing studies.
    """

    total_fixed_mass: float  # i.e.. avionics, propulsion, landing gear; g
    as_mass_ratio: float  # aerostructural mass ratio
    lift_to_drag_ratio: float  # this will turn into a function of speed eventually
    cruise_speed: float  # m/s, currently not sensitive to this
    turn_speed: float  # m/s
    propulsive_efficiency: float
    configuration_bonus: float = 1.0
    short_takeoff: bool = False
    stability_distance: float = 0


@dataclass
class PlanformParameters(SerializableParameters):
    """
    Planform shape parameters for Night Fury.

    Blended wing body with wing sweep.

    """

    name: str

    # Centerbody dimensions
    centerbody_halfspan: float
    centerbody_chord: float

    # Midbody dimensions
    midbody_y: float
    midbody_xle: float
    midbody_chord: float

    # Wing
    wing_root_le: float
    wing_root_chord: float
    wing_halfspan: float
    wing_taper_ratio: float
    wing_root_le_sweep_angle: float

    # Control surfaces
    ctrl_surface_start_y: float
    ctrl_surface_end_y: float
    ctrl_surface_x_over_c: float  # how far it creeps up the end of the wing


@dataclass
class WingSizingParameters(SerializableParameters):
    takeoff_power: float
    takeoff_thrust: float
    aspect_ratio: float
    sweep_angle: float
    airfoil_cl_max: float
    s_wet_s_ref: float
    c_fe: float
    cruise_speed: float
    turn_speed: float
    stall_speed: float
    oswald_efficiency: float
    takeoff_headwind: float
    takeoff_distance: float
    ground_cl: float
    rolling_resistance_coefficient: float
