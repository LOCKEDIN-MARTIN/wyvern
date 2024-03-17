from typing import Callable, NamedTuple

import numpy as np
from scipy.integrate import cumtrapz


class BeamDerivatives(NamedTuple):
    """
    Named tuple for beam derivatives
    """

    shear_force: np.ndarray
    bending_moment: np.ndarray
    slope: np.ndarray
    deflection: np.ndarray
    bending_stress: np.ndarray  # My/I
    shear_stress: np.ndarray  # VQ/It


def beam_derivatives(
    lift_distr: Callable[[float], float],
    y: np.ndarray,
    b: float,
    h: np.ndarray,
    E: float,
) -> BeamDerivatives:
    """
    Calculate cantilevered beam SFD, BMD, Slope, Deflection
    """
    ell = lift_distr(y)

    # SFD
    shear_force = cumtrapz(-ell * np.sign(y), y, initial=0)
    shear_force = shear_force - shear_force[-1]

    # BMD
    bending_moment = cumtrapz(-shear_force * np.sign(y), y, initial=0)
    bending_moment = bending_moment - bending_moment[-1]

    # find zero point
    idx_0 = np.argmin(np.abs(y))

    # Slope
    I = (b * h**3) / 12
    Q = b * h**2 / 8
    slope = cumtrapz(bending_moment / (E * I), y, initial=0)
    slope = slope - slope[idx_0]

    # Deflection
    deflection = cumtrapz(slope, y, initial=0)
    deflection = deflection - deflection[idx_0]

    # Stresses
    bending_stress = bending_moment * h / (2 * I)
    shear_stress = shear_force * Q / (I * b)

    return BeamDerivatives(
        shear_force, bending_moment, slope, deflection, bending_stress, shear_stress
    )
