import numpy as np

from wyvern.utils.constants import RHO, G


def crazy_takeoff_func(
    C_Lmax: float,
    C_D0: float,
    mu: float,
    v_hw: float,
    s_TO: float,
    T: float,
    W: float,
    C_Lgr: float,
    AR: float,
    e: float,
) -> float:
    """
    Wing loading estimate for takeoff performance

    Parameters
    ----------
    C_Lmax : float
        Maximum lift coefficient of the entire aircraft
    C_D0 : float
        Zero-lift drag coefficient of the entire aircraft
    mu : float
        Ground friction coefficient (0.05-0.1 normal)
    v_hw : float
        Headwind velocity (m/s)
    s_TO : float
        Takeoff ground run (m)
    T : float
        Takeoff thrust (N)
    W : float
        Aircraft weight (N)
    C_Lgr : float
        Lift coefficient at takeoff rotation
    AR : float
        Aspect ratio of the wing
    e : float
        Oswald efficiency factor of the wing

    Returns
    -------
    float
        Wing loading (kg/m^2)

    Algorithm
    ---------
    Uses method derived from AER406 tutorial 2
    """

    C4 = -(1.15**2) / (G * RHO * C_Lmax)
    C3 = 1.15 * v_hw / G * np.sqrt(2 / (RHO * C_Lmax))
    C2 = s_TO * (
        T / W
        + 1.15**2 / (2 * C_Lmax) * (mu * C_Lgr - C_D0 - C_Lgr**2 / (np.pi * e * AR))
        - mu
    ) - v_hw**2 / (2 * G)
    C1 = 0
    C0 = s_TO * (RHO * v_hw**2 / 4) * (mu * C_Lgr - C_D0 - C_Lgr**2 / (np.pi * e * AR))

    results = np.polynomial.polynomial.polyroots([C0, C1, C2, C3, C4])
    # pick correct root
    return results[3] ** 2 / G
