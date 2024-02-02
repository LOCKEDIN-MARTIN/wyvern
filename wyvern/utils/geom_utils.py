import numpy as np
import numpy.typing as npt


def centroid_of_polyshape(points: npt.NDArray[np.floating]):
    """
    Returns the centroid of a set of points defining a polygonal shape.
    array shape: (n, 2)
    """

    # https://stackoverflow.com/a/2792459/3628998
    # https://stackoverflow.com/questions/2792443/finding-the-centroid-of-a-polygon

    x, y = points.T
    area = 0.5 * np.sum(x * np.roll(y, 1) - y * np.roll(x, 1))
    cx = (1 / (6 * area)) * np.sum(
        (x + np.roll(x, 1)) * (x * np.roll(y, 1) - y * np.roll(x, 1))
    )
    cy = (1 / (6 * area)) * np.sum(
        (y + np.roll(y, 1)) * (x * np.roll(y, 1) - y * np.roll(x, 1))
    )

    return cx, cy


def area_of_points(points: npt.NDArray[np.floating]):
    """
    Returns the area of a set of points defining a polygonal shape.
    array shape: (n, 2)

    Polygon can be concave, so use a triangulation method.
    """

    # https://stackoverflow.com/a/30408825/3628998
    # https://stackoverflow.com/questions/30405648/computing-area-of-irregular-polygon-in-python

    x, y = points.T

    return 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))


def sweep_angle_along_chord(
    taper_ratio: float,
    ar: float,
    calc_x_c: float,
    ref_sweep: float,
    ref_x_c: float = 0,
) -> float:
    """
    Given the sweep angle at a certain point along a tapered wing,
    calculate the sweep angle at any other point along the chord.

    Parameters
    ----------
    taper_ratio : float
        Taper ratio of the wing (0 < taper_ratio < 1).
        equal to c_tip / c_root
    ar : float
        Aspect ratio of the wing.
    calc_x_c : float
        Chordwise position to calculate the sweep angle at.
    ref_sweep : float
        Sweep angle at the reference point, in degrees.
    ref_x_c : float, optional
        Chordwise position of the reference point, by default 0 (leading edge).

    Returns
    -------
    float
        Sweep angle at the calculated point, in degrees.

    """

    return np.degrees(
        np.arctan(
            np.tan(np.radians(ref_sweep))
            - 4 / ar * (calc_x_c - ref_x_c) * (1 - taper_ratio) / (1 + taper_ratio)
        )
    )
