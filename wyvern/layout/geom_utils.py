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
