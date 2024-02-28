import os
from pathlib import Path
import subprocess
# import multiprocessing as mp

def main():
    path = Path("cases")
    cases = os.listdir(path)
    # cpus = os.cpu_count()

    for case in cases:
        subprocess.run([path/case/"Allrun"])
        break

    # run_cases = [[path/case/"Allrun"] for case in cases]
    # with mp.Pool(processes=cpus) as p:
    #     p.map(subprocess.run, run_cases)

if __name__ == "__main__":
    main()