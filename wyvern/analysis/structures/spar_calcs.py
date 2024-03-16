from typing import Callable, NamedTuple

import numpy as np


class BeamDerivatives(NamedTuple):
    """
    Named tuple for beam derivatives
    """

    shear_force: np.ndarray
    bending_moment: np.ndarray
    slope: np.ndarray
    deflection: np.ndarray


def beam_derivatives(
    lift_distr: Callable[[float], float], y: np.ndarray
) -> BeamDerivatives:
    """
    Calculate cantilevered beam SFD, BMD, Slope, Deflection
    """
