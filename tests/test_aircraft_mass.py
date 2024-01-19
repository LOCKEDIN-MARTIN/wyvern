from wyvern.data.components import ALL_COMPONENTS
from wyvern.sizing.aircraft_mass import total_component_mass
import pytest


def test_fixed_mass():
    assert total_component_mass(ALL_COMPONENTS) == pytest.approx(448.15)
