from pathlib import Path
import shutil
from itertools import product
from string import Template
from typing import Tuple
import tomli
import numpy as np
from numpy.typing import NDArray

def replicate_template_directory(template_path: Path, case_path: Path) -> None:
    shutil.copytree(template_path, case_path, dirs_exist_ok=True)

def populate_verticies(b1z, b1x, b1y, b2z, b2x, b2y, 
                           swz1, swx, swy, swz2, template) -> str:

    building_verticies = template.substitute(b1x0=-0.5*swx-b1x, 
                                             b1x1=-0.5*swx, 
                                             b1y0=-b1y, 
                                             b1z1=b1z,
                                             b2x0=0.5*swx, 
                                             b2x1=0.5*swx+b2x, 
                                             b2y0=-b2y, 
                                             b2z1=b2z,
                                             swx0=-0.5*swx, 
                                             swx1=0.5*swx, 
                                             swy0=-swy,
                                             swz0=swz2,
                                             swz1=swz1+swz2,)
    
    return building_verticies

def write_snappy_hex_mesh_dict(beginning:str, ending:str, building_verticies: str, path: Path) -> None:
    with open(path/"snappyHexMeshDict", "w") as f:
        f.writelines(beginning)
        f.write(building_verticies)
        f.writelines(ending)

def populate_boundary_conditions(deg: int, abl_template, initial_template) -> Tuple[str]:
    n = unit_vec(deg)
    u0 = 0.001*n
    abl = abl_template.substitute(nx=n[0], ny=n[1])
    init = initial_template.substitute(ux=u0[0], uy=u0[1])
    return abl, init

def write_boundary_conditions(path: Path, abl, init) -> None:

    with open(path/"ABLConditions", "w") as f:
        f.write(abl)

    with open(path/"initialConditions", "w") as f:
        f.write(init)

def unit_vec(deg: int) -> NDArray:
    """
    Returns unit vector pointing in direction from given degrees.
    deg = 0 is defined as (0,-1,0)
    """
    alpha = np.radians(deg)
    return -np.array((np.sin(alpha), np.cos(alpha), 0))

def main() -> None:

    with open("config.toml", "rb") as f:
        config = tomli.load(f)

    case_path = Path(config["case_path"])
    template_path = Path(config["template_path"])

    building_template = Template(config["building_template"])
    abl_template = Template(config["abl_template"])
    initial_template = Template(config["initial_template"])

    # Generate all combinations of dimensions
    dimensions = [value for value in config["dimensions"].values()]

    with open(template_path/"system/snappyHexMeshDict.beginning", "r") as f:
        beginning = f.readlines()
    with open(template_path/"system/snappyHexMeshDict.ending", "r") as f:
        ending = f.readlines()

    # Create case file for each combination
    for inflow_deg in np.arange(0, 360, config["inflow_increment"]):
        abl, init = populate_boundary_conditions(inflow_deg, abl_template, initial_template)
        for i, dimension_combination in enumerate(product(*dimensions)):
            replicate_template_directory(template_path, case_path/f"{inflow_deg}/case_{i}")
            building_verticies = populate_verticies(*dimension_combination, building_template)
            write_snappy_hex_mesh_dict(beginning, ending, building_verticies, case_path/f"{inflow_deg}/case_{i}/system")
            write_boundary_conditions(case_path/f"{inflow_deg}/case_{i}/0/include", abl, init)

if __name__ == "__main__":
    main()