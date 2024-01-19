from wyvern.data.payloads import PAYLOADS
import numpy as np
from pandas import DataFrame


def total_component_mass(components: DataFrame) -> float:
    """Total masses from components list.

    Parameters
    ----------
    component : DataFrame
        Dataframe of components

    Returns
    -------
    float
        Total mass of fixed components.

    """
    return sum(
        components["basic_mass"] * (1 + components["mga_pct"] / 100) * components["qty"]
    )


def payload_mass(payload_config: tuple[int]) -> float:
    """Payload mass from payload configuration.

    Parameters
    ----------
    payload_config : tuple[int]
        Number of each payload carried.

    Returns
    -------
    float
        Total payload mass.
    """
    # Take linear combination of payload_config with PAYLOADS["mass"]
    return np.dot(payload_config, PAYLOADS["mass"])


def total_mass(
    payload_config: tuple[int], as_mass_ratio: float, total_fixed_mass: float
) -> float:
    """Total mass of aircraft.

    Parameters
    ----------
    payload_config : tuple[int]
        Number of each payload carried.
    as_mass_ratio : float
        Aerostructural mass ratio.
    total_fixed_mass : float
        Total fixed mass of avionics and propulsion components.

    Returns
    -------
    float
        Total mass of aircraft.

    Formulas
    --------
    W_0 = \frac{W_{\text{payload}} + W_{\text{propulsion}} + W_{\text{avionics}} }{ 1 - W_{\text{aerostructure}} / W_0}

    where W_{\text{propulsion}} + W_{\text{avionics}} = total_fixed_mass
    """
    return (payload_mass(payload_config) + total_fixed_mass) / (1 - as_mass_ratio)
