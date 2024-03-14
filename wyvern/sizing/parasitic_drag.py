import subprocess
from pathlib import Path

import numpy as np
from scipy.integrate import quad

from wyvern.utils.constants import MU, RHO


def cd0_zeroth_order(c_fe: float, s_wet_s_ref) -> float:
    """Estimate the parasitic drag coefficient using a crude method.

    Parameters
    ----------
    c_fe : float
        Skin friction coefficient.
    s_wet_s_ref : float
        Wetted area to wing area ratio.

    Returns
    -------
    float
        parasitic drag coefficient.
    """
    return c_fe * s_wet_s_ref


def cfe_turbulent(re: float) -> float:
    """Estimate the skin friction coefficient for turbulent flow.

    Parameters
    ----------
    re : float
        Reynolds number.

    Returns
    -------
    float
        Skin friction coefficient.
    """
    return 0.455 / (np.log10(re) ** 2.58)


def cfe_xfoil(re: list[float], sections: list[np.ndarray]) -> list[float]:
    """Estimate the skin friction coefficient using xfoil.

    Parameters
    ----------
    re : list[float]
        List of Reynolds numbers.
    sections : list[str]
        List of airfoil sections.

    Returns
    -------
    list[float]
        List of skin friction coefficients.
    """

    cfe = []
    # run xfoil
    for i, re_i in enumerate(re):

        input_path = (
            Path(__file__).parent.parent / "data/standalone_xfoil/xfoil_input.txt"
        )

        with open(input_path, "w") as f:

            # suppress plot
            f.write("PLOP\n")
            f.write("G\n")
            f.write("\n")

            if sections[i] == "NACA":
                f.write("NACA 0018\n")
            else:
                f.write("LOAD BOEING.dat\n")
                f.write("BOEING VERTOL\n")
                # refine panelling
                f.write("PPAR\n")
                f.write("N 300\n")
                f.write("\n")
                f.write("\n")

            f.write("OPER\n")
            f.write("ITER 200\n")
            f.write(f"VISC {re_i}\n")
            f.write("VPAR\n")
            # set xtr
            f.write("XTR 0.1 0.1\n")
            f.write("\n")
            # set mach to 0.02
            f.write("MACH 0.02\n")
            f.write("CL 0\n")

            f.write("\n")
            f.write("quit\n")

        out_str = subprocess.check_output(
            ["xfoil.exe", "<", "xfoil_input.txt"],
            shell=True,
            cwd=Path(__file__).parent.parent / "data/standalone_xfoil",
        )
        # find the last line of the output
        out_str = out_str.decode("utf-8").split("\n")
        for line in out_str[::-1]:
            # Looking for an entry with the pattern "CD = 1.23456    =>"
            if "CD" in line:
                # find where "CD" is, read ahead 11 chars
                cfe_i = float(line[line.find("CD") + 4 : line.find("CD") + 16])
                break

        print(f"Station {i} done. cfe: {cfe_i:5f}")
        cfe.append(cfe_i)

    return cfe


def _area_integrand(
    y: float, y_stations: np.ndarray, c: np.ndarray, sections: list[np.ndarray]
) -> float:
    """Integrand for the wetted area calculation."""
    # determine sectional properties
    c_i = np.interp(y, y_stations, c)

    # determine section by nearest neighbour
    section_i = sections[np.argmin(np.abs(y - y_stations))] * c_i
    section_x = section_i[:, 0]
    section_y = section_i[:, 1]

    # get arc length
    dx = np.diff(section_x)
    dy = np.diff(section_y)
    ds = np.sqrt(dx**2 + dy**2)
    return np.sum(ds)


def _drag_integrand(
    y: float,
    y_stations: np.ndarray,
    c: np.ndarray,
    sections: list[np.ndarray],
    sweep_ang: np.ndarray,
    v: float,
    all_outputs: bool = False,
) -> float:
    """Integrand for the drag calculation."""
    # determine sectional properties
    c_i = np.interp(y, y_stations, c)
    sweep_i = np.interp(y, y_stations, sweep_ang)

    # determine section by nearest neighbour
    section_i = sections[np.argmin(np.abs(y - y_stations))] * c_i
    section_y = section_i[:, 1]

    tcmax = np.max(section_y) - np.min(section_y)

    # get arc length
    s = _area_integrand(y, y_stations, c, sections)

    Re_i = RHO * v * c_i / MU

    # skin friction and form factor
    cf_i = cfe_turbulent(Re_i)

    Q_i = abs(y) / max(y_stations) * 0.4 + 1  # interference factor

    k_i = 1 + 2 * np.cos(np.pi / 180 * sweep_i) * tcmax + 100 * tcmax**4

    if all_outputs:
        return c_i, sweep_i, tcmax, s, Re_i, cf_i, k_i, Q_i
    return cf_i * s * k_i * Q_i


def cd0_buildup(
    y_stations: np.ndarray,
    c: np.ndarray,
    sections: list[np.ndarray],
    sweep_ang: np.ndarray,
    v: float,
    S_ref: float,
) -> tuple[float, float]:
    """Estimate the parasitic drag coefficient using a more detailed method."""

    # smoothly integrate from one station to the next

    def area_integrand(y: float):
        return _area_integrand(y, y_stations, c, sections)

    def drag_integrand(y: float):
        return _drag_integrand(y, y_stations, c, sections, sweep_ang, v)

    # integrate
    wetted_area = quad(area_integrand, y_stations[0], y_stations[-1], epsrel=1e-6)[0]
    CD0 = quad(drag_integrand, y_stations[0], y_stations[-1], epsrel=1e-6)[0] / S_ref

    return CD0, wetted_area
