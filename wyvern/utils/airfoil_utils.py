from io import StringIO


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
