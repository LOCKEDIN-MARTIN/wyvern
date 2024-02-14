from io import StringIO


def naca_4d_to_tikz(naca_4d: str, num_points: int = 100) -> str:
    """
    Convert a NACA 4-digit airfoil to a .tikz file.

    Args:
        naca_4d: The NACA 4-digit airfoil.
        num_points: The number of points to interpolate.

    Returns:
        The string of the .tikz file.
    """
    m = int(naca_4d[0]) / 100
    p = int(naca_4d[1]) / 10
    t = int(naca_4d[2:]) / 100
    c = 1
    x = [c * i / (num_points - 1) for i in range(num_points)]

    # densify points near the leading edge
    for i in range(num_points):
        x[i] = x[i] ** 2

    y = [0] * num_points

    for i in range(num_points):
        if x[i] < p:
            y[i] = m * x[i] / (p**2) * (2 * p - x[i])
        else:
            y[i] = m * (c - x[i]) / ((1 - p) ** 2) * (1 + x[i] - 2 * p)

    y_t = [0] * num_points
    y_b = [0] * num_points
    for i in range(num_points):
        y_t[i] = y[i] + t / 0.2 * c * (
            0.2969 * x[i] ** 0.5
            - 0.1260 * x[i]
            - 0.3516 * x[i] ** 2
            + 0.2843 * x[i] ** 3
            - 0.1015 * x[i] ** 4
        )
        y_b[i] = y[i] - t / 0.2 * c * (
            0.2969 * x[i] ** 0.5
            - 0.1260 * x[i]
            - 0.3516 * x[i] ** 2
            + 0.2843 * x[i] ** 3
            - 0.1015 * x[i] ** 4
        )

    buf = StringIO()
    buf.write(r"\begin{scope}[y=-1cm, x=1cm]")
    buf.write("\n")
    buf.write(r"\draw[thick] ")
    for i in range(num_points):
        if i != 0:
            buf.write(" -- ")
        buf.write(f"({x[i]},{y_t[i]})")
    for i in range(num_points - 1, -1, -1):
        buf.write(" -- ")
        buf.write(f"({x[i]},{y_b[i]})")
    buf.write(" -- cycle;")
    buf.write("\n")
    buf.write(r"\end{scope}")
    return buf.getvalue()


def dat_to_tikz(dat_string: str) -> str:
    """
    Convert a .dat file to a .tikz file.

    Args:
        dat_string: The string of the .dat file.

    Returns:
        The string of the .tikz file.
    """
    buf = StringIO()

    lines = dat_string.split("\n")
    buf.write(r"\begin{scope}[y=-1cm, x=1cm]")
    buf.write("\n")
    buf.write(r"\draw[thick] ")

    for i, line in enumerate(lines):
        if not line:
            continue
        if i != 0:
            buf.write(" -- ")
        x, y = line.split()
        buf.write(f"({x},{y})")

    buf.write(" -- cycle;")
    buf.write("\n")
    buf.write(r"\end{scope}")
    return buf.getvalue()
