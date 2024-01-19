import pandas as pd
from wyvern.sizing import (
    total_mass,
    payload_mass,
    total_component_mass,
    aerostructural_mass_ratio,
)
from wyvern.metrics import cargo_units


def sweep_payload_configs(
    payload_configs: list[tuple[int]],
    components: pd.DataFrame,
    historical_ref: pd.DataFrame,
) -> pd.DataFrame:
    """Sweep payload configurations.

    Parameters
    ----------
    payload_configs : list[tuple[int]]
        List of payload configurations.
    components : pd.DataFrame
        Dataframe of components.
    historical_ref : pd.DataFrame
        Dataframe of historical reference configurations.

    Returns
    -------
    pd.DataFrame
        Dataframe of payload configurations and performance figures.
    """
    results = {}

    # Compute constants
    total_fixed_mass = total_component_mass(components)
    as_mass_ratio = aerostructural_mass_ratio(historical_ref, total_fixed_mass)

    for config in payload_configs:
        payload_mass_ = payload_mass(config)
        total_mass_ = total_mass(config, as_mass_ratio, total_fixed_mass)
        empty_mass_ = total_mass_ - payload_mass_

        payload_fraction = payload_mass_ / total_mass_
        as_mass = as_mass_ratio * total_mass_
        cargo_units_ = cargo_units(config)

        reached_pf_cap = payload_fraction > 0.25

        payload_score = cargo_units_**0.7 * min(0.25, payload_fraction)

        results[config] = {
            "payload_mass": payload_mass_,
            "empty_mass": empty_mass_,
            "as_mass": as_mass,
            "takeoff_mass": total_mass_,
            "cargo_units": cargo_units_,
            "payload_fraction": payload_fraction,
            "reached_pf_cap": reached_pf_cap,
            "payload_score": payload_score,
        }

    return pd.DataFrame(results).T
