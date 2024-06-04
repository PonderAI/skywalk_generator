# Code to clean and process the images into model training data
import os
from pathlib import Path
import tomli
import numpy as np
from scipy.ndimage import rotate
import matplotlib.pyplot as plt


with open("config.toml", "rb") as f:
        CONFIG = tomli.load(f)

def generate_geometry_data(l_building_height, sky_walk_height, r_building_height, building_mask, clim_max=100, mask_value=0):
    # Create dummy array to cookie cutter buildings
    cookie_cutter_array = np.ones((1024, 1024))

    # Set building heights
    cookie_cutter_array[:, :504] *= l_building_height/clim_max 
    cookie_cutter_array[:, 504:520] *= sky_walk_height/clim_max
    cookie_cutter_array[:, 520:] *= r_building_height/clim_max

    # Set all non-building pixels to zero
    cookie_cutter_array[building_mask] = mask_value

    # Remove corners
    cookie_cutter_array[:, :200] = mask_value 
    cookie_cutter_array[:, 800:] = mask_value
    
    return cookie_cutter_array

def rotate_image(img, angle, cnr_mask):

    theta = np.deg2rad(angle)
    mask = np.all(img <= [0.004,0.004,0.004], axis=-1)
    img -= 0.5
    img[:,:,0], img[:,:,1] = img[:,:,0] * np.cos(theta) + img[:,:,1] * -np.sin(theta), img[:,:,0] * np.sin(theta) + img[:,:,1] * np.cos(theta)
    img += 0.5
    img[mask] = [0.5, 0.5, 0.5]
    img[cnr_mask] = [0.5, 0.5, 0.5]
    img = rotate(img, angle=angle, reshape=False)

    return img

def process_case(case, case_path, output_path, cnr_mask):

    angle = int(case.split("_")[-1])

    geom = plt.imread(f"{output_path/case}_geom.png")
    geom = geom[:,:,0]
    building_mask = np.where(geom > 0.004)
    

    # Get z dimensions of buildings from snappyHexMeshDict
    with open(case_path/case/"system/snappyHexMeshDict", "r") as f:
        text = f.readlines()
    
    dimensions = [t for t in text if "min  (" in t or "max  (" in t]
    b1_min, b1_max, b2_min, b2_max, sw_min, sw_max = [int(d.split(" ")[-1].strip(");\n")) for d in dimensions]
    top = generate_geometry_data(b1_max, sw_max, b2_max, building_mask)
    bottom = generate_geometry_data(b1_max, sw_min, b2_min, building_mask)
    bottom_inverted = generate_geometry_data(100 - b1_max, 100 - sw_min, 100 - b2_min, building_mask, mask_value=1)

    top = rotate(top, angle=angle, reshape=False)
    bottom = rotate(bottom, angle=angle, reshape=False)
    bottom_inverted = rotate(bottom_inverted, angle=angle, reshape=False)

    vfield = plt.imread(f"{output_path/case}.png")
    vfield = rotate_image(vfield, angle, cnr_mask)

    np.save(f"{output_path/case}_geom_top", top)
    np.save(f"{output_path/case}_geom_bottom", bottom) 
    np.save(f"{output_path/case}_geom_bottom_inv", bottom_inverted) 
    np.save(output_path/case, vfield) 

def main():

    case_path = Path(CONFIG["case_path"])
    output_path = Path(CONFIG["output_path"])

    Path.mkdir(output_path, exist_ok=True)
    cases = os.listdir(case_path)
    cnr_mask = np.load(CONFIG["cnr_mask"])

    for case in cases:
        process_case(case, case_path, output_path, cnr_mask)
        break

if __name__ == "__main__":
     main()