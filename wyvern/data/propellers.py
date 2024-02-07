from pathlib import Path

import numpy as np


class PropellerCurve:
    def __init__(self, name: str, data: np.ndarray):
        self.name = name
        self._data = data

    @property
    def v(self):
        return self._data[0, :]

    @property
    def T(self):
        return self._data[1, :]

    @property
    def P(self):
        return self.T * self.v


# all models assume 20 mAh discharge
PROP_8X8 = PropellerCurve(
    "8x8",
    np.loadtxt(
        Path(__file__).parent / "sources/prop_8x8_d20.csv",
        delimiter=",",
    ),
)

PROP_9X6 = PropellerCurve(
    "9x6",
    np.loadtxt(
        Path(__file__).parent / "sources/prop_9x6_d20.csv",
        delimiter=",",
    ),
)

PROP_10X5 = PropellerCurve(
    "10x5",
    np.loadtxt(
        Path(__file__).parent / "sources/prop_10x5_d20.csv",
        delimiter=",",
    ),
)
