import os
from pathlib import Path
import subprocess
import tomli
# import multiprocessing as mp

def main():

    with open("config.toml", "rb") as f:
        config = tomli.load(f)

    case_path = Path(config["case_path"])

    path = Path(case_path)
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