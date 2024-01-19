import pandas as pd
from wyvern.sizing import (
    total_mass,
    payload_mass,
    total_component_mass,
    aerostructural_mass_ratio,
)
from wyvern.metrics import cargo_units
from wyvern.data import ALL_COMPONENTS
from wyvern.metrics.scoring import _flight_score_factors
from wyvern.performance.energy import energy_consumption
from wyvern.analysis.parameters import AssumedParameters


def sweep_payload_configs(
    payload_configs: list[tuple[int]],
    params: AssumedParameters,
    historical_ref: pd.DataFrame,
    components: pd.DataFrame = ALL_COMPONENTS,
) -> pd.DataFrame:
    """Sweep payload configurations.

    Parameters
    ----------
    payload_configs : list[tuple[int]]
        List of payload configurations.
    params : AssumedParameters
        Parameters for the analysis.
    historical_ref : pd.DataFrame
        Dataframe of historical reference configurations.
    components : pd.DataFrame
        Dataframe of components, by default ALL_COMPONENTS.

    Returns
    -------
    pd.DataFrame
        Dataframe of payload configurations and performance figures.
    """
    results = {}

    # Compute constants
    total_fixed_mass = total_component_mass(components)
    as_mass_ratio = aerostructural_mass_ratio(historical_ref, total_fixed_mass)

    print(
        f"Total Fixed Mass: {total_fixed_mass:.2f} g\n"
        f"AS Mass Ratio: {as_mass_ratio*100:.3f}%"
    )

    # Do Sweep
    for config in payload_configs:
        payload_mass_ = payload_mass(config)
        total_mass_ = total_mass(config, as_mass_ratio, total_fixed_mass)
        empty_mass_ = total_mass_ - payload_mass_

        payload_fraction = payload_mass_ / total_mass_
        as_mass = as_mass_ratio * total_mass_
        cargo_units_ = cargo_units(config)

        reached_pf_cap = payload_fraction > 0.25

        total_energy = (
            energy_consumption(
                total_mass_,
                params.cruise_speed,
                params.turn_speed,
                params.lift_to_drag_ratio,
            )
            / params.propulsive_efficiency
        )

        (
            cargo_score,
            efficiency_score,
            pf_score,
            tb_score,
            cb_score,
            stb_score,
        ) = _flight_score_factors(config, params, historical_ref, components)

        results[config] = {
            "payload_mass": payload_mass_,
            "empty_mass": empty_mass_,
            "as_mass": as_mass,
            "takeoff_mass": total_mass_,
            "cargo_units": cargo_units_,
            "payload_fraction": payload_fraction,
            "reached_pf_cap": reached_pf_cap,
            "cargo_score_times_pf": cargo_score * pf_score,
            "total_energy": total_energy,
            "efficiency_score": efficiency_score,
            "takeoff_bonus": tb_score,
            "configuration_bonus": cb_score,
            "stability_bonus": stb_score,
            "total_flight_score": cargo_score
            * efficiency_score
            * pf_score
            * tb_score
            * cb_score
            * stb_score,
        }

    return pd.DataFrame(results).T
