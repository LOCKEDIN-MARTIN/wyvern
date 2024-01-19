from wyvern.data import PAYLOADS, ALL_COMPONENTS
import numpy as np
from warnings import warn
import pandas as pd
from wyvern.performance.energy import energy_consumption
from wyvern.sizing import (
    total_mass,
    aerostructural_mass_ratio,
    total_component_mass,
    payload_mass,
)

from wyvern.analysis.parameters import AssumedParameters


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
    params: AssumedParameters,
    historical_ref: pd.DataFrame,
    components: pd.DataFrame = ALL_COMPONENTS,
) -> tuple[float]:
    """
    Objective Function
    ------------------
    \Phi = \gamma ^{0.7}\times\left(\frac{3200}{E}\right)^2\times\min(\mathrm{PF}, 0.25)\times\mathrm{TB}\times\mathrm{CB}\times\mathrm{STB}

    The separate multiplicative factors are returned.
    """
    gamma = cargo_units(payload_config)
    cargo_score = gamma**0.7

    total_fixed_mass = total_component_mass(components)
    as_ratio = aerostructural_mass_ratio(historical_ref, total_fixed_mass)

    payload_mass_ = payload_mass(payload_config)
    mass = total_mass(payload_config, as_ratio, total_fixed_mass)

    energy = (
        energy_consumption(
            mass, params.cruise_speed, params.turn_speed, params.lift_to_drag_ratio
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
    params: AssumedParameters,
    historical_ref: pd.DataFrame,
    components: pd.DataFrame = ALL_COMPONENTS,
) -> float:
    """
    Flight score as a function of payload configuration.

        Parameters
        ----------
        payload_config : tuple[int]
            Number of each payload carried.
        historical_ref : pd.DataFrame
            Historical reference configurations.
        components : pd.DataFrame
            Components.
        params : AssumedParameters
            Assumed parameters.

        Returns
        -------
        float
            Flight score.
    """
    factors = _flight_score_factors(payload_config, params, historical_ref, components)
    return np.prod(factors)
