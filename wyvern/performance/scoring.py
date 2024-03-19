from warnings import warn

import numpy as np

from wyvern.analysis.parameters import PayloadSizingParameters
from wyvern.data import PAYLOADS
from wyvern.performance.energy import energy_consumption
from wyvern.sizing import (
    payload_mass,
    total_mass,
)


def cargo_units(payload_config: tuple[int]) -> int:
    """Total cargo units from payload configuration.

    Parameters
    ----------
    payload_config : tuple[int]
        Number of each payload carried.

    Returns
    -------
    int
        Total cargo units.

    Warns
    -----
    If payload configuration is invalid.
    i.e. cu < 100 or cu > 800
    """
    cu = np.dot(payload_config, PAYLOADS["points"])

    if cu < 100 or cu > 800:
        warn(
            f"Payload configuration {payload_config} has {cu} CU,"
            " which is out of range [100, 800]."
        )

    return cu


def _flight_score_factors(
    payload_config: tuple[int],
    params: PayloadSizingParameters,
) -> tuple[float]:
    """
    Objective Function
    ------------------
    \Phi = \gamma ^{0.7}\times\left(\frac{3200}{E}\right)^2\times\min(\mathrm{PF}, 0.25)\times\mathrm{TB}\times\mathrm{CB}\times\mathrm{STB}

    The separate multiplicative factors are returned.
    """
    gamma = cargo_units(payload_config)
    cargo_score = gamma**0.7

    payload_mass_ = payload_mass(payload_config)
    mass = total_mass(payload_config, params.as_mass_ratio, params.total_fixed_mass)

    energy = (
        sum(
            energy_consumption(
                mass,
                params.cruise_speed,
                params.turn_speed,
                params.aero_model,
                params.planform_area,
            )
        )
        / params.propulsive_efficiency
    )

    efficiency_score = (3200 / energy) ** 2

    payload_fraction = payload_mass_ / mass
    pf_score = min(0.25, payload_fraction)

    # bonuses
    tb_score = 1.25 if params.short_takeoff else 1.0
    cb_score = params.configuration_bonus
    stb_score = 1 + 0.2 * np.clip(params.stability_distance, 0, 100) / 100

    return (cargo_score, efficiency_score, pf_score, tb_score, cb_score, stb_score)


def flight_score(
    payload_config: tuple[int],
    params: PayloadSizingParameters,
) -> float:
    """
    Flight score as a function of payload configuration.

        Parameters
        ----------
        payload_config : tuple[int]
            Number of each payload carried.
        params : AssumedParameters
            Assumed parameters for analysis.

        Returns
        -------
        float
            Flight score.
    """
    factors = _flight_score_factors(payload_config, params)
    return np.prod(factors)
