import subprocess

# xfoil script

re_numbers = [373868, 287591, 191727, 164885, 138044, 111202, 84360, 57518]
sections = ["NACA", "NACA", "BOEING", "BOEING", "BOEING", "BOEING", "BOEING", "BOEING"]

for i in range(len(re_numbers)):
    with open("xfoil_input.txt", "w") as f:

        f.write("Y\n")  # load default settings

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
        f.write(f"VISC {re_numbers[i]}\n")
        f.write("PACC\n")
        f.write(f"output_{i}.txt\n")
        f.write(f"dump_{i}.dmp\n")
        f.write("aseq 11 17 0.1\n")
        f.write("\n")
        f.write("quit\n")

    # run xfoil
    subprocess.run(["xfoil.exe", "<", "xfoil_input.txt"], shell=True)
