from dataclasses import dataclass
from typing import Any

import numpy as np

from wyvern.utils.constants import RHO, G


@dataclass
class QuadraticLDModel:
    """
    Quadratic lift and drag model for aircraft performance analysis.

    C_D = C_D0 + k * C_L^2

    Attributes
    ----------
    c_d0 : float
        Zero-lift drag coefficient
    e_inviscid : float
        Inviscid span efficiency factor (0.95+)
    K : float
        Sweep-dependent correction factor from shevell
        0.38 for 0 sweep, 0.4 for 20 deg, 0.45 for 35 deg
    aspect_ratio : float
        Aspect ratio of the entire aircraft
    """

    c_d0: float
    e_inviscid: float
    K: float
    aspect_ratio: float

    @property
    def e(self):
        """
        Oswald efficiency factor, taking into account viscous drag
        contributions
        """
        return 1 / (
            1 / (self.e_inviscid) + np.pi * self.K * self.aspect_ratio * self.c_d0
        )

    @property
    def kappa(self):
        return 1 / (np.pi * self.aspect_ratio * self.e)

    @property
    def c_d_ldmax(self):
        return self.c_d0 * 2

    @property
    def c_l_ldmax(self):
        return np.sqrt(self.c_d0 / self.kappa)

    @property
    def l_d_max(self):
        return self.c_l_ldmax / self.c_d_ldmax

    def v_ldmax(self, wing_loading_Nm2: float):
        """
        Estimate the speed at which maximum lift-to-drag ratio occurs.

        Parameters
        ----------
        wing_loading_Nm2 : float
            Wing loading in N/m^2
        """
        return np.sqrt(2 * wing_loading_Nm2 / (RHO * self.c_l_ldmax))

    def v_prmin(self, wing_loading_Nm2: float):
        """
        Estimate the speed at which minimum power required occurs.

        Parameters
        ----------
        wing_loading_Nm2 : float
            Wing loading in N/m^2
        """
        return np.sqrt(
            2
            * wing_loading_Nm2
            / (RHO * np.sqrt(3 * np.pi * self.aspect_ratio * self.e * self.c_d0))
        )

    def v_trmin(self, wing_loading_Nm2: float):
        """
        Estimate the speed at which minimum thrust required occurs.

        Parameters
        ----------
        wing_loading_Nm2 : float
            Wing loading in N/m^2
        """
        return self.v_ldmax(wing_loading_Nm2)

    def c_D(self, c_L: float):
        """
        Estimate the drag coefficient given a lift coefficient.
        """
        return self.c_d0 + self.kappa * c_L**2

    def c_L(self, c_D: float):
        """
        Estimate the lift coefficient given a drag coefficient.
        """
        return np.sqrt((c_D - self.c_d0) / self.kappa)


class CNSTLDModel(QuadraticLDModel):
    """
    Dummy class spoofing a constant lift-drag model for more
    basic analyses.
    """

    # fake the constructor to set all the parameters to 0
    def __init__(self, ld: float, *args: Any, **kwargs: Any):
        self.ld = ld
        super().__init__(0, 0, 0, 0)

    def c_D(self, c_L: float):
        return c_L / self.ld

    def __str__(self) -> str:
        return str(self.ld)
