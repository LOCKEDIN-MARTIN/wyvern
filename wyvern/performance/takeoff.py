import numpy as np


def crazy_takeoff_func(
    C_Lmax,
    C_D0,
    mu,
    v_hw,
    s_TO,
    T,
    W,
    C_Lgr,
    AR,
    e,
) -> float:
    g0 = 9.80665
    rho = 1.225

    C4 = -(1.05**2) / (g0 * rho * C_Lmax)
    C3 = 1.05 * v_hw / g0 * np.sqrt(2 / (rho * C_Lmax))
    C2 = s_TO * (
        T / W
        + 1.05**2 / (2 * C_Lmax) * (mu * C_Lgr - C_D0 - C_Lgr**2 / (np.pi * e * AR))
        - mu
    ) - v_hw**2 / (2 * g0)
    C1 = 0
    C0 = (
        s_TO
        * (rho * v_hw**2 / 4)
        * (mu * C_Lgr - C_D0 - C_Lgr**2 / (np.pi * e * AR))
    )

    results = np.polynomial.polynomial.polyroots([C0, C1, C2, C3, C4])
    # pick correct root
    return results[3] ** 2 / g0
