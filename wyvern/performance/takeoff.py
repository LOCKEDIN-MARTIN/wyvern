from typing import Callable

import numpy as np
from scipy.integrate import quad

from wyvern.data.propellers import PropellerCurve
from wyvern.performance.models import QuadraticLDModel
from wyvern.utils.constants import RHO, G


def thrust_crude(v: float):
    """
    Crude quadratic model that matches tutorial slides
    """
    # 7.5 N static thrust
    # about 3 N of thrust at 20 m/s
    T = -0.006 * v**2 - 0.1 * v + 7.5
    return T


def prop_thrust(prop_model: PropellerCurve):
    """
    Propeller thrust model
    """

    # generate interpolant
    def thrust(v: float):
        v_clamped = np.clip(v, min(prop_model.v), max(prop_model.v))
        return np.interp(v_clamped, prop_model.v, prop_model.T)

    return thrust


def ground_roll_sweep(
    v_hw: float,
    v_max: float,
    aero_model: QuadraticLDModel,
    mass: float,
    mu: float,
    CLgr: float,
    thrust_model: Callable[[float], float],
) -> tuple[np.ndarray, np.ndarray]:
    v_lo_series = np.linspace(v_hw, v_max, 100)

    s_series = np.array(
        [
            takeoff_distance(v_hw, v_lo, aero_model, mass, mu, CLgr, thrust_model)
            for v_lo in v_lo_series
        ]
    )

    return v_lo_series, s_series


def takeoff_distance(
    v_hw: float,
    v_lo: float,
    aero_model: QuadraticLDModel,
    mass: float,
    mu: float,
    CLgr: float,
    thrust_model: Callable[[float], float],
) -> float:
    """
    Numerical integration based takeoff distance calculation.

    Parameters
    ----------
    v_hw: float
        Headwind speed, m/s
    v_max: float
        Maximum takeoff speed, m/s
    aero_model: QuadraticLDModel
        Lift and drag model
    mass: float
        Vehicle mass, kg
    mu: float
        Rolling resistance coefficient
    CLgr: float
        Ground lift coefficient
    thrust_model: Callable[[float], float]
        Thrust model

    Returns
    -------
    v_lo_series: np.ndarray
        Takeoff speed series
    s_series: np.ndarray
        Takeoff distance series

    """

    # these correlations are currently speed-independent
    # needs additional corrections for Re variations
    def lift(v: float):
        return 1 / 2 * RHO * v**2 * CLgr

    def normal_force(v: float):
        return mass * G - lift(v)

    def friction(v: float):
        return normal_force(v) * mu

    def drag(v: float):
        return 1 / 2 * RHO * v**2 * aero_model.c_D(CLgr)

    def integrand(v: float):
        return mass * (v - v_hw) / (thrust_model(v) - drag(v) - friction(v))

    return quad(integrand, v_hw, v_lo)[0]
