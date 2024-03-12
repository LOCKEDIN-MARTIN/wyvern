import subprocess
from pathlib import Path

import numpy as np

from wyvern.utils.constants import MU, RHO

root_dir = Path(__file__).parent.parent.parent

# aircraft parameters
ctrl_y = np.array([0, 92.5, 185, 850]) * 1e-3  # m
# Wing chord
ctrl_c = np.array([780, 600, 400, 120]) * 1e-3  # m

y_stations = np.array([0, 92.5, 185, 318, 451, 584, 717, 850]) * 1e-3  # m

v = 7  # m/s

c_stations = np.interp(y_stations, ctrl_y, ctrl_c)

re_stations = RHO * v * c_stations / MU

# run xfoil in sequence

last_airfoil = None
must_reload = True


input_path = root_dir / "wyvern/data/standalone_xfoil/xfoil_input.txt"

# delete any "output*.txt" files
for f in root_dir.glob("wyvern/data/standalone_xfoil/output_*.txt"):
    f.unlink()

with open(input_path, "w") as f:

    f.write("PLOP\n")
    f.write("G\n")
    f.write("\n")

    for i in range(len(re_stations)):

        # Load airfoil based on y location
        y_i = y_stations[i]
        re_i = re_stations[i]

        must_reload = (y_i < 185e-3 and last_airfoil != "NACA") or (
            y_i >= 185e-3 and last_airfoil != "BOEING"
        )

        if must_reload:
            # start from "main menu" and go to oper mode
            f.write("visc\n")  # exit visc oper mode if we have to
            f.write("\n")  # quit oper mode if we are in it
            if y_i < 185e-3 and last_airfoil != "NACA":
                f.write("NACA 0018\n")
                last_airfoil = "NACA"
            elif last_airfoil != "BOEING":
                f.write("LOAD BOEINGopen.dat\n")
                f.write("BOEING VERTOL\n")
                last_airfoil = "BOEING"
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
            # set ncrit = 4
            f.write("n\n")
            f.write("4\n")
            f.write("\n")
            # set mach to 0.02
            f.write("MACH 0.02\n")
        else:
            # start from oper mode already in visc
            f.write(f"RE {re_i}\n")

        # get pacc file
        f.write("PACC\n")
        f.write(f"output_{i}.txt\n")
        f.write("\n")  # no dump file

        # alpha sweep to find max cl

        f.write("aseq 11 17 0.1\n")

        # turn off pacc
        f.write("PACC\n")

    f.write("\n")
    f.write("quit\n")

# run xfoil
subprocess.run(
    ["xfoil.exe", "<", "xfoil_input.txt"],
    shell=True,
    cwd=root_dir / "wyvern/data/standalone_xfoil",
)


# then, read the output files and process the data
clmax = np.zeros(len(re_stations))
alphastall = np.zeros(len(re_stations))
for i in range(len(re_stations)):
    with open(root_dir / f"wyvern/data/standalone_xfoil/output_{i}.txt", "r") as f:
        lines = f.readlines()

    # process the data
    # find the first line that starts with "  -"
    for j in range(len(lines)):
        if lines[j].startswith("  -"):
            start = j
            break

    arr = np.genfromtxt(lines[start:], skip_header=1, skip_footer=1)

    alpha = arr[:, 0]
    cl = arr[:, 1]

    # find max cl and print it along with the corresponding alpha
    idx = np.argmax(cl)
    print(f"Max cl for section {i} is {cl[idx]} at alpha = {alpha[idx]}")

    clmax[i] = cl[idx]
    alphastall[i] = alpha[idx]

# write the data to a file
np.savetxt(
    "clmax.txt",
    np.column_stack((y_stations, re_stations, clmax, alphastall)),
    header="y re clmax alphastall",
)
