from pathlib import Path
import shutil
from string import Template
import logging
from itertools import product
from typing_extensions import Annotated
import tomli
import numpy as np
from numpy.typing import NDArray
from pyDOE import lhs
import typer
from functools import cache

logging.basicConfig(level=logging.INFO,
                    format="%(levelname)s %(message)s",)

def replicate_template_directory(template_path: Path, case_path: Path) -> None:
    shutil.copytree(template_path, case_path, dirs_exist_ok=True)

def populate_verticies(b1z1, b1x, b1y1, b1z2, b1y2,
                       b2z1, b2x, b2y1, b2z2, b2y2, 
                       swz1, swx, swy, swz2, template) -> str:
    
    # Skip nonsense dimension combinations
    if b1y2 >= b2y1 or b2y2 >= b1y1:
        return False

    building_verticies = template.substitute(b1x0=-0.5*swx-b1x, 
                                             b1x1=-0.5*swx, 
                                             b1y0=-b1y1-b1y2, 
                                             b1y1=-b1y2, 
                                             b1z0=b1z2,
                                             b1z1=b1z1-b1z2,
                                             b2x0=0.5*swx, 
                                             b2x1=0.5*swx+b2x, 
                                             b2y0=-b2y1-b2y2, 
                                             b2y1=-b2y2, 
                                             b2z0=b2z2,
                                             b2z1=b2z1-b2z2,
                                             swx0=-0.5*swx, 
                                             swx1=0.5*swx, 
                                             swy0=-swy - max(b1y2, b2y2),
                                             swy1=-max(b1y2, b2y2),
                                             swz0=swz2,
                                             swz1=swz1+swz2,)
    
    return building_verticies

def write_snappy_hex_mesh_dict(beginning:str, ending:str, building_verticies: str, path: Path) -> None:
    with open(path/"snappyHexMeshDict", "w") as f:
        f.writelines(beginning)
        f.write(building_verticies)
        f.writelines(ending)

def write_boundary_conditions(deg: int, abl_template, initial_template, path: Path) -> None:
    n = unit_vec(deg)
    u0 = 0.001*n
    abl = abl_template.substitute(nx=n[0], ny=n[1])
    init = initial_template.substitute(ux=u0[0], uy=u0[1])

    with open(path/"ABLConditions", "w") as f:
        f.write(abl)

    with open(path/"initialConditions", "w") as f:
        f.write(init)

@cache
def unit_vec(deg: int) -> NDArray:
    """
    Returns unit vector pointing in direction from given degrees.
    deg = 0 is defined as (0,-1,0)
    """
    alpha = np.radians(deg)
    return -np.array((np.sin(alpha), np.cos(alpha), 0))

def main(samples: Annotated[int, typer.Argument()] = None) -> None:

    with open("config.toml", "rb") as f:
        config = tomli.load(f)

    case_path = Path(config["case_path"])
    template_path = Path(config["template_path"])

    building_template = Template(config["building_template"])
    abl_template = Template(config["abl_template"])
    initial_template = Template(config["initial_template"])

    with open(template_path/"system/snappyHexMeshDict.beginning", "r") as f:
        beginning = f.readlines()
    with open(template_path/"system/snappyHexMeshDict.ending", "r") as f:
        ending = f.readlines()

    # Latin hypercube sampling
    if samples is not None:
        dimension_levels = np.array([len(levels) - 1 for levels in config["dimensions"].values()])
        if samples > np.prod(dimension_levels + 1):
            logging.error(f"Cannot create more than {np.prod(dimension_levels + 1):,} samples with this combination of dimension levels")
            return
        lhs_samples = lhs(n=len(config["dimensions"]), samples=samples)

        i = 0 # Not using enumerate as case numbers get skipped
        for lhs_sample in lhs_samples:
            dimension_indices = (lhs_sample * dimension_levels).round().astype(int)
            dimension_combination = [config["dimensions"][k][i] for k, i in zip(config["dimensions"].keys(), dimension_indices)]
            building_verticies = populate_verticies(*dimension_combination, building_template)
            if not building_verticies:
                continue
            i += 1 
            for inflow_deg in np.arange(0, 360, config["inflow_increment"]):
                replicate_template_directory(template_path, case_path/f"case_{i}_{inflow_deg}")
                write_snappy_hex_mesh_dict(beginning, ending, building_verticies, case_path/f"case_{i}_{inflow_deg}/system")
                write_boundary_conditions(inflow_deg, abl_template, initial_template, case_path/f"case_{i}_{inflow_deg}/0/include")
        
        logging.info(f"{i} samples generated, {samples - i} samples with impossible combinations of dimensions skipped")

    else:
        dimensions = [value for value in config["dimensions"].values()]
        i = 0
        for dimension_combination in product(*dimensions):
            building_verticies = populate_verticies(*dimension_combination, building_template)
            if not building_verticies:
                continue
            i += 1
            for inflow_deg in np.arange(0, 360, config["inflow_increment"]):
                replicate_template_directory(template_path, case_path/f"case_{i}_{inflow_deg}")
                write_snappy_hex_mesh_dict(beginning, ending, building_verticies, case_path/f"case_{i}_{inflow_deg}/system")
                write_boundary_conditions(inflow_deg, abl_template, initial_template, case_path/f"case_{i}_{inflow_deg}/0/include")

        logging.info(f"{i} samples generated")

if __name__ == "__main__":
    typer.run(main)