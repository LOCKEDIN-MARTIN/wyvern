from wyvern.data.payloads import PAYLOADS
import numpy as np
from warnings import warn


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


def flight_score(payload_config: tuple[int]) -> float:
    gamma = cargo_units(payload_config)
