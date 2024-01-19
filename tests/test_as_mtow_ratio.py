import pytest

from wyvern.data.historical import RASSAM_CORRELATIONS
from wyvern.sizing.as_mtow_ratio import aerostructural_mass_ratio


def test_as_mtow_ratio_nominal():
    assert aerostructural_mass_ratio(RASSAM_CORRELATIONS, 448.15) == pytest.approx(
        0.45262566421
    )
