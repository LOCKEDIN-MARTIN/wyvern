import numpy as np
import pytest

from wyvern.utils.geom_utils import area_of_points, centroid_of_polyshape


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
