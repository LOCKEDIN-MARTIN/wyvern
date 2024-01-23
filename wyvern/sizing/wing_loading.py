import numpy as np
from pandas import DataFrame

from wyvern.analysis.parameters import WingSizingParameters


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
        Dataframe of W/S and P/W estimates in different flight conditions.
        units of kg/m^2 and W/lb respectively.
    """
