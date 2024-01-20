from dataclasses import dataclass
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from io import StringIO


@dataclass
class PlanformParameters:
    """
    Planform shape parameters for Night Fury.

    Blended wing body with wing sweep.

    """

    name: str

    # Centerbody dimensions
    centerbody_halfspan: float
    centerbody_chord: float

    # Midbody dimensions
    midbody_y: float
    midbody_xle: float
    midbody_chord: float

    # Wing
    wing_root_le: float
    wing_root_chord: float
    wing_halfspan: float
    wing_taper_ratio: float
    wing_root_le_sweep_angle: float

    # Control surfaces
    ctrl_surface_start_y: float
    ctrl_surface_end_y: float
    ctrl_surface_x_over_c: float  # how far it creeps up the end of the wing


NF_844_A = PlanformParameters(
    name="NF-844-A",
    centerbody_halfspan=175,
    centerbody_chord=650,
    midbody_y=140,
    midbody_xle=100,
    midbody_chord=500,
    wing_root_le=300,
    wing_root_chord=300,
    wing_halfspan=600,
    wing_taper_ratio=0.33,
    wing_root_le_sweep_angle=40,
    ctrl_surface_start_y=500,
    ctrl_surface_end_y=700,
    ctrl_surface_x_over_c=0.3,
)


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
        }
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


def plotting_coords_from_planform(df: pd.DataFrame) -> np.ndarray:
    """
    Convert a planform DataFrame into a set of coordinates for plotting.

    The DataFrame must have the following columns:

    - Y
    - XLE
    - XTE

    The DataFrame must be sorted by Y ascending.
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


def planform_stats(configuration: PlanformParameters) -> pd.DataFrame:
    """
    Compute the following properties of the planform:
    - Aspect ratio
    - Centroid
    """


def viz_planform(configuration: PlanformParameters):
    """
    Visualize the planform.
    """
    df = planform_span_stations(configuration)

    pts = plotting_coords_from_planform(df)

    plt.plot(pts[:, 0], pts[:, 1], label="planform")
    plt.gca().invert_yaxis()
    plt.axis("equal")
    plt.title(configuration.name)
    plt.xlabel("Y (mm)")
    plt.ylabel("X (mm)")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    df = planform_span_stations(NF_844_A)
    print(span_stations_to_avl(df))
    viz_planform(NF_844_A)
