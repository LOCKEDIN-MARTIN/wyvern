import numpy as np
from pandas import DataFrame

from wyvern.analysis.parameters import WingSizingParameters
from wyvern.sizing.parasitic_drag import cd0_zeroth_order
from wyvern.sizing.takeoff import crazy_takeoff_func
from wyvern.utils.constants import RHO, G


def aircraft_cl_max_estimate(sweep_angle: float, airfoil_cl_max: float):
    """
    Estimate the maximum coefficient of lift of the aircraft.

    CL_max = 0.9 * CL_max_airfoil * cos(sweep_angle)
    """
    return 0.9 * airfoil_cl_max * np.cos(np.radians(sweep_angle))


def wing_loading_estimate(
    params: WingSizingParameters, takeoff_mass: float
) -> DataFrame:
    """Estimate wing loading.

    Parameters
    ----------
    params : WingSizingParameters
        Parameters for the analysis.
    takeoff_mass : float
        Takeoff mass.

    Returns
    -------
    DataFrame
        Dataframe of W/S values for stall, cruise and takeoff.
    """
    CL_max = aircraft_cl_max_estimate(params.sweep_angle, params.airfoil_cl_max)
    CD0 = cd0_zeroth_order(params.c_fe, params.s_wet_s_ref)

    weight = takeoff_mass / 1000 * G  # N

    # stall wing loading
    q_stall = 0.5 * RHO * params.stall_speed**2
    ws_stall = q_stall * CL_max / G  # kg/m^2

    # cruise wing loading
    q_cruise = 0.5 * RHO * params.cruise_speed**2
    ld_max = (
        1 / 2 * np.sqrt(np.pi * params.aspect_ratio * params.oswald_efficiency / CD0)
    )

    ws_cruise = (
        q_cruise
        * np.sqrt(CD0 * np.pi * params.oswald_efficiency * params.aspect_ratio)
        / G
    )  # kg/m^2

    # takeoff
    ws_takeoff = crazy_takeoff_func(
        CL_max,
        CD0,
        params.rolling_resistance_coefficient,
        params.takeoff_headwind,
        params.takeoff_distance,
        params.takeoff_thrust,
        weight,
        params.ground_cl,
        params.aspect_ratio,
        params.oswald_efficiency,
    )

    df = DataFrame(
        {
            "W/S": [ws_stall, ws_cruise, ws_takeoff],
        },
        index=["Stall", "Cruise", "Takeoff"],
    )

    return df
