import numpy as np

# then, read the output files and process the data
for i in range(8):
    with open(f"output_{i}.txt", "r") as f:
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
