import numpy as np
from pandas import DataFrame

from wyvern.analysis.parameters import WingSizingParameters
from wyvern.performance.takeoff import crazy_takeoff_func


def aircraft_cl_max_estimate(sweep_angle: float, airfoil_cl_max: float):
    """
    Estimate the maximum coefficient of lift of the aircraft.

    CL_max = 0.9 * CL_max_airfoil * cos(sweep_angle)
    """
    return 0.9 * airfoil_cl_max * np.cos(np.radians(sweep_angle))


def cd0_estimate(c_fe: float, s_wet_s_ref) -> float:
    """Estimate the parasitic drag coefficient using a crude method.

    Parameters
    ----------
    c_fe : float
        Skin friction coefficient.
    s_wet_s_ref : float
        Wetted area to wing area ratio.

    Returns
    -------
    float
        parasitic drag coefficient.
    """
    return c_fe * s_wet_s_ref


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
    rho = 1.225  # kg/m^3
    CL_max = aircraft_cl_max_estimate(params.sweep_angle, params.airfoil_cl_max)
    CD0 = cd0_estimate(params.c_fe, params.s_wet_s_ref)

    g0 = 9.80665

    weight = takeoff_mass / 1000 * g0  # N

    # stall wing loading
    q_stall = 0.5 * rho * params.stall_speed**2
    ws_stall = q_stall * CL_max / g0  # kg/m^2

    # cruise wing loading
    q_cruise = 0.5 * rho * params.cruise_speed**2
    ld_max = (
        1 / 2 * np.sqrt(np.pi * params.aspect_ratio * params.oswald_efficiency / CD0)
    )

    ws_cruise = (
        q_cruise
        * np.sqrt(CD0 * np.pi * params.oswald_efficiency * params.aspect_ratio)
        / g0
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


def power_to_weight(
    ws_values: DataFrame,
):
    pass
