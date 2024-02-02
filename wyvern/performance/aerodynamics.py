import numpy as np
from pandas import DataFrame

from wyvern.analysis.parameters import PlanformParameters, WingSizingParameters
from wyvern.layout import planform_stats
from wyvern.performance.energy import course_lengths
from wyvern.performance.flight_regimes import generate_flight_regimes
from wyvern.sizing.parasitic_drag import cd0_zeroth_order


def flight_estimates_week_2(
    wing_sizing: WingSizingParameters, planform: PlanformParameters, takeoff_mass: float
):
    """

    Parameters
    ----------
    flight_regimes: DataFrame
        DataFrame containing flight regimes and their corresponding parameters
    """
    flight_regimes = generate_flight_regimes(wing_sizing)

    aircraft_weight = takeoff_mass / 1000 * 9.80665  # N

    lift_per_regime = aircraft_weight * flight_regimes["load_factor"]

    # planform metrics
    planform_stats_ = planform_stats(planform)
    total_area = planform_stats_["overall_area"].values
    overall_span = planform_stats_["overall_span"].values / 1000
    wing_mac = planform_stats_["wing_mean_aerodynamic_chord"].values / 1000
    centerbody_chord = planform.centerbody_chord / 1000

    # estimate CL using crude methods
    aircraft_CL = lift_per_regime / flight_regimes["dynamic_pressure"] / total_area

    # rough lift distribution approximation
    lift_per_span_wing = lift_per_regime / overall_span
    lift_per_span_centerline = (
        lift_per_span_wing * 4 / np.pi
    )  # rectangle with same area as ellipse; height

    centerbody_cl = (
        lift_per_span_centerline / centerbody_chord / flight_regimes["dynamic_pressure"]
    )
    wing_cl = lift_per_span_wing / wing_mac / flight_regimes["dynamic_pressure"]

    # estimate CD using crude methods
    cd0 = cd0_zeroth_order(wing_sizing.c_fe, wing_sizing.s_wet_s_ref)
    aircraft_CD = (
        cd0
        + aircraft_CL**2
        / np.pi
        / wing_sizing.aspect_ratio
        / wing_sizing.oswald_efficiency
    )

    # estimate thrust required
    thrust_required = total_area * flight_regimes["dynamic_pressure"] * aircraft_CD

    lift_to_drag = aircraft_CL / aircraft_CD

    # estimate power required
    power_required = thrust_required * flight_regimes["speed"]
    power_consumed = power_required / 0.5  # hardcoded for now

    aircraft_weight_lb = takeoff_mass / 1000 * 2.20462  # lb

    p_w_ratio = power_consumed / aircraft_weight_lb  # W/lb

    straight_length, turn_length = course_lengths()

    # energy = lift / L/D * distance / efficiency

    energy_cruise = lift_per_regime[2] / lift_to_drag[2] * straight_length / 0.5
    energy_turn = lift_per_regime[1] / lift_to_drag[1] * turn_length / 0.5

    df = DataFrame(
        {
            "CL": aircraft_CL,
            "CD": aircraft_CD,
            "centerbody_Cl": centerbody_cl,
            "wing_Cl": wing_cl,
            "thrust_required": thrust_required,
            "power_required": power_required,
            "power_consumed": power_consumed,
            "lift_to_drag": lift_to_drag,
            "p_w_ratio": p_w_ratio,
            "energy_consumption": [0, energy_turn, energy_cruise, 0],
        },
        index=flight_regimes.index,
    )
    return df
