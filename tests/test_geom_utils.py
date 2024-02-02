import numpy as np
import pytest

from wyvern.utils.geom_utils import (
    area_of_points,
    centroid_of_polyshape,
    sweep_angle_along_chord,
)


def test_centroid_of_polyshape():
    polygon = np.array(
        [
            (0, 0),
            (70, 0),
            (70, 25),
            (45, 45),
            (45, 180),
            (95, 188),
            (95, 200),
            (-25, 200),
            (-25, 188),
            (25, 180),
            (25, 45),
            (0, 25),
        ],
    )
    assert centroid_of_polyshape(polygon) == pytest.approx((35.0, 100.46145125))


def test_area_of_points():
    polygon = np.array(
        [[0, 0], [10, 0], [10, 10], [0, 10]],
    )
    assert area_of_points(polygon) == pytest.approx(100.0)


def test_sweep_angle_along_chord():
    taper_ratio = 0.8329422983
    le_sweep = 64.7890871
    qc_sweep = 63.91877902
    ar = 1.123689329

    assert sweep_angle_along_chord(taper_ratio, ar, 0.25, le_sweep, 0) == pytest.approx(
        qc_sweep
    )
