from copy import copy
from typing import Sequence

import pandas as pd
from matplotlib import pyplot as plt

from wyvern.analysis.parameters import PayloadSizingParameters
from wyvern.performance.energy import energy_consumption
from wyvern.performance.scoring import _flight_score_factors, cargo_units
from wyvern.sizing import (
    payload_mass,
    total_mass,
)


def sweep_payload_configs(
    payload_configs: list[tuple[int]],
    params: PayloadSizingParameters,
) -> pd.DataFrame:
    """Sweep payload configurations.

    Parameters
    ----------
    payload_configs : list[tuple[int]]
        List of payload configurations.
    params : AssumedParameters
        Parameters for the analysis.

    Returns
    -------
    pd.DataFrame
        Dataframe of payload configurations and performance figures.
    """
    results = {}

    # Do Sweep
    for config in payload_configs:
        payload_mass_ = payload_mass(config)
        total_mass_ = total_mass(config, params.as_mass_ratio, params.total_fixed_mass)
        empty_mass_ = total_mass_ - payload_mass_

        payload_fraction = payload_mass_ / total_mass_
        as_mass = params.as_mass_ratio * total_mass_
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
        ) = _flight_score_factors(config, params)

        results[config] = {
            "num_ping_pong_balls": config[0],
            "num_golf_balls": config[1],
            "num_tennis_balls": config[2],
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


def sensitivity_plot(
    payload_configs: list[tuple[int]],
    params: PayloadSizingParameters,
    sensitivity: str,
    sensitivity_range: Sequence[float],
):
    """
    Plots the flight scores for various payload configurations under varying
    values of a given parameter.

    Parameters
    ----------
    payload_configs : list[tuple[int]]
        List of payload configurations.
    params : AssumedParameters
        Parameters for the analysis. (baseline)
    sensitivity : str
        Name of the parameter to vary.
    sensitivity_range : Sequence[float]
        List of values to vary the parameter over.
    """

    # make a big dataframe
    def do_sweep_at_param(param_value):
        params_ = copy(params)
        params_.__dict__[sensitivity] = param_value
        df_ = sweep_payload_configs(payload_configs, params_)
        df_["sensitivity"] = param_value
        return df_

    dfs = [do_sweep_at_param(param_value) for param_value in sensitivity_range]

    # plot flight score wrt # golf balls for each param value
    fig, ax = plt.subplots()
    for df, sens_value in zip(dfs, sensitivity_range):
        ax.plot(
            df["num_golf_balls"],
            df["total_flight_score"],
            label=f"{sens_value}",
            marker="o",
        )
    ax.set_xlabel("Number of Golf Balls")
    ax.set_ylabel("Flight Score")
    ax.legend()
    ax.grid()
    plt.title(f"Flight Score vs. Payload Config\nfor Varying '{sensitivity}'")
    plt.show()
