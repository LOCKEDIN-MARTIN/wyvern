from io import StringIO

import numpy as np
import pandas as pd

from wyvern.analysis.parameters import PlanformParameters
from wyvern.utils.geom_utils import area_of_points, centroid_of_polyshape


def planform_span_stations(conf: PlanformParameters) -> pd.DataFrame:
    """
    Calculate the spanwise stations of the planform.

    Output format (compatible with AVL):

    | Y | XLE | Chord | XTE | Hinge line |
    """

    y = np.array(
        [
            0,
            conf.midbody_y,
            conf.centerbody_halfspan,
            conf.ctrl_surface_start_y,
            conf.ctrl_surface_end_y,
            conf.wing_halfspan + conf.centerbody_halfspan,
        ]
    )

    # Control surface calculations
    x_le_wingtip = (
        np.tan(np.deg2rad(conf.wing_root_le_sweep_angle)) * conf.wing_halfspan
        + conf.wing_root_le
    )

    y_it = np.array(
        [conf.centerbody_halfspan, conf.centerbody_halfspan + conf.wing_halfspan]
    )
    x_it = np.array([conf.wing_root_le, x_le_wingtip])
    chord_tip = conf.wing_root_chord * conf.wing_taper_ratio
    chord_it = np.array([conf.wing_root_chord, chord_tip])

    # lerp between the two points to get control surface x_le and chord
    x_le_cts_start = np.interp(conf.ctrl_surface_start_y, y_it, x_it)
    x_le_cts_end = np.interp(conf.ctrl_surface_end_y, y_it, x_it)
    chord_cts_start = np.interp(conf.ctrl_surface_start_y, y_it, chord_it)
    chord_cts_end = np.interp(conf.ctrl_surface_end_y, y_it, chord_it)

    # hinge line calculations, at distance x_over_c from the trailing edge
    x_hinge_start = x_le_cts_start + chord_cts_start * (1 - conf.ctrl_surface_x_over_c)
    x_hinge_end = x_le_cts_end + chord_cts_end * (1 - conf.ctrl_surface_x_over_c)

    xle = np.array(
        [
            0,
            conf.midbody_xle,
            conf.wing_root_le,
            x_le_cts_start,
            x_le_cts_end,
            x_le_wingtip,
        ]
    )
    chord = np.array(
        [
            conf.centerbody_chord,
            conf.midbody_chord,
            conf.wing_root_chord,
            chord_cts_start,
            chord_cts_end,
            chord_tip,
        ]
    )

    hinge_line = np.array([np.nan, np.nan, np.nan, x_hinge_start, x_hinge_end, np.nan])

    # sanity check
    xte = xle + chord

    df = pd.DataFrame(
        {
            "Y": y,
            "XLE": xle,
            "chord": chord,
            "XTE": xte,
            "hinge_line": hinge_line,
        },
        index=[
            "center",
            "midbody",
            "wing_root",
            "ctrl_surface_start",
            "ctrl_surface_end",
            "wing_tip",
        ],
    )

    return df


def span_stations_to_avl(df: pd.DataFrame) -> str:
    """
    Convert a DataFrame of span stations to inputs for the AVL
    analysis tool.

    AVL docs: https://web.mit.edu/drela/Public/web/avl/avl_doc.txt

    CONTROL                              | (keyword)
    elevator  1.0  0.6   0. 1. 0.   1.0  | name, gain,  Xhinge,  XYZhvec,  SgnDup


    The CONTROL keyword declares that a hinge deflection at this section
    is to be governed by one or more control variables.  An arbitrary number
    of control variables can be used, limited only by the array limit NDMAX.

    SECTION
    0.0  0.0  0.0   2.0   0.0   | Xle Yle Zle   Chord Ainc
    """
    # aircraft is of a standard format, so it's not too hard to figure out
    # the AVL input format

    buf = StringIO()

    # Iterate through each row of the DataFrame
    # if the row does not have a hinge line, only the SECTION keyword is needed
    # if the row does have a hinge line, the CONTROL keyword is needed

    for _, row in df.iterrows():
        # SECTION keyword
        buf.write(f"SECTION\n" f"{row.XLE} {row.Y} 0.0 {row.chord} 0.0\n")

        # CONTROL keyword
        if not np.isnan(row.hinge_line):
            buf.write(f"CONTROL\n" f"elevon 1.0 {row.hinge_line} 0. 1. 0. 1.0\n")

    return buf.getvalue()


def span_stations_to_tikz(df: pd.DataFrame) -> str:
    """
    Convert a DataFrame of span stations to TikZ code for plotting.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame of span stations.

    Returns
    -------
    str
        TikZ code for plotting.
    """
    buf = StringIO()

    pts = full_planform_points(df) / 100

    # plot the planform
    buf.write(r"\begin{scope}[y=-1cm, x=1cm]")
    buf.write("\n")
    buf.write(r"\draw[thick] ")
    for i, (x, y) in enumerate(pts):
        if i == 0:
            buf.write(f"({x}, {y}) ")
        else:
            buf.write(f"-- ({x}, {y}) ")
    buf.write(";\n")
    buf.write(r"\end{scope}")

    return buf.getvalue()


def full_planform_points(df: pd.DataFrame) -> np.ndarray:
    """
    Convert a planform DataFrame into a set of coordinates for plotting.

    The DataFrame must have the following columns:

    - Y
    - XLE
    - XTE

    The DataFrame must be sorted by Y ascending.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame representing the planform. Each row represents a point
        on the planform, and each column represents a property of the point.

    Returns
    -------
    np.ndarray
        A 2D numpy array of coordinates. Each row of the array represents
        a point on the planform, and the two columns represent the x and y
        coordinates of the point.
    """

    # first, plot (y, xle) and afterwards (y, xte)
    # such that they connect to form a closed shape

    # must symmetrically reflect the xte points across the xle points
    pts_le_1 = df[["Y", "XLE"]].values
    pts_le_2 = pts_le_1.copy()[::-1]
    pts_le_2[:, 0] = -pts_le_2[:, 0]
    pts_te_1 = df[["Y", "XTE"]].values[::-1]
    pts_te_2 = pts_te_1.copy()[::-1]
    pts_te_2[:, 0] = -pts_te_2[:, 0]

    # join the points together
    pts = np.concatenate([pts_le_1, pts_te_1, pts_te_2, pts_le_2])

    return pts


def wing_points(df: pd.DataFrame) -> np.ndarray:
    """
    Gets just the wing coordinates (single-sided).
    """
    # only need to get the wing portion
    wing = df.loc["wing_root":"wing_tip"]

    # first, plot (y, xle) and afterwards (y, xte)
    # such that they connect to form a closed shape
    pts_le = wing[["Y", "XLE"]].values
    pts_te = wing[["Y", "XTE"]].values[::-1]

    return np.concatenate([pts_le, pts_te])


def centerbody_points(df: pd.DataFrame) -> np.ndarray:
    """
    Gets just the centerbody coordinates (single-sided).
    """
    # only need to get the wing portion
    centerbody = df.loc["center":"wing_root"]

    # first, plot (y, xle) and afterwards (y, xte)
    # such that they connect to form a closed shape
    pts_le = centerbody[["Y", "XLE"]].values
    pts_te = centerbody[["Y", "XTE"]].values[::-1]

    return np.concatenate([pts_le, pts_te])


def control_surface_points(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """
    Gets just the control surface coordinates (dual-sided).
    """
    ctl_surface_pts = np.array(
        [
            [
                df.loc["ctrl_surface_start", "Y"],
                df.loc["ctrl_surface_start", "hinge_line"],
            ],
            [df.loc["ctrl_surface_end", "Y"], df.loc["ctrl_surface_end", "hinge_line"]],
        ]
    )
    # mirror the control surface points
    ctl_surface_pts_mirror = ctl_surface_pts.copy()
    ctl_surface_pts_mirror[:, 0] = -ctl_surface_pts_mirror[:, 0]

    return ctl_surface_pts, ctl_surface_pts_mirror


def planform_stats(configuration: PlanformParameters) -> pd.DataFrame:
    """
    Compute the following properties of the planform:
    - Aspect ratio
    - Centroid
    """
    df = planform_span_stations(configuration)

    # full aircraft
    # aspect ratio
    overall_span = df.Y.max() * 2
    overall_ar = overall_span**2 / area_of_points(full_planform_points(df))

    full_pts = full_planform_points(df)
    overall_centroid = centroid_of_polyshape(full_pts)

    # just wings
    wing_pts = wing_points(df)
    wing_span = wing_pts[:, 0].max() - wing_pts[:, 0].min()
    wing_ar = wing_span**2 / area_of_points(wing_pts) * 2
    # multiply by 2 because two wing halves
    wing_centroid = centroid_of_polyshape(wing_pts)

    # just centerbody
    cb_pts = centerbody_points(df)
    cb_span = cb_pts[:, 0].max() - cb_pts[:, 0].min()
    cb_ar = cb_span**2 / area_of_points(cb_pts) * 2
    cb_centroid = centroid_of_polyshape(cb_pts)

    # areas
    area = area_of_points(full_pts) / 1e6
    cb_area = area_of_points(cb_pts) / 1e6
    wing_area = area_of_points(wing_pts) / 1e6

    # wing mean aerodynamic chord
    # trapezoidal wing, so use a simplified formulation
    c_root = configuration.wing_root_chord
    c_tip = c_root * configuration.wing_taper_ratio
    wing_mac = 2 / 3 * (c_root + c_tip - c_root * c_tip / (c_root + c_tip))

    # overall mean aerodynamic chord - wing area / wing span
    span = (cb_span + wing_span) * 2
    overall_mac = area * 1e6 / span

    return pd.DataFrame(
        {
            "overall_area": area,
            "overall_span": overall_span,
            "overall_mean_aerodynamic_chord": overall_mac,
            "overall_aspect_ratio": overall_ar,
            "overall_centroid": overall_centroid[1],
            "wing_span": wing_span,
            "wing_half_area": wing_area,
            "wing_mean_aerodynamic_chord": wing_mac,
            "wing_aspect_ratio": wing_ar,
            "wing_centroid": wing_centroid[1],
            "centerbody_span": cb_span,
            "centerbody_half_area": cb_area,
            "centerbody_aspect_ratio": cb_ar,
            "centerbody_centroid": cb_centroid[1],
        },
        index=[configuration.name],
    )
