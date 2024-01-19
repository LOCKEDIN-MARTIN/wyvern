from pandas import DataFrame


def aerostructural_mass_ratio(
    historical_configs: DataFrame, total_fixed_mass: float
) -> float:
    """Calculate the average aerostructural mass ratio of aircraft based on historical data.

    Parameters
    ----------
    historical_configs : DataFrame
        A DataFrame containing historical aircraft configurations.
    total_fixed_mass : float
        The total fixed mass of the aircraft.

    Returns
    -------
    float
        The average aerostructural mass ratio of aircraft based on historical data.

    """
    aerostructural_mass = historical_configs["EW (g)"] - total_fixed_mass
    total_mass = historical_configs["Max Wt (g)"]
    return (aerostructural_mass / total_mass).mean()
