# Code to convert the CFD data to images
import os
from pathlib import Path
import tomli
import numpy as np
import pyvista as pv
from PIL import Image
from matplotlib.colors import ListedColormap

def save_field(output_path, mesh, field, clim):

    scale = 650
    p = pv.Plotter(off_screen=True, window_size=[1024, 1024])

    vals = np.ones((256, 3))
    vals[:, 1] = np.linspace(0, 1, 256)
    cmap = ListedColormap(vals)
    
    p.add_mesh(mesh, show_edges=False, scalars=field, lighting=False, show_scalar_bar=False, cmap=cmap, clim=clim)
    p.enable_parallel_projection()
    p.view_xy()
    p.set_background([1,1,1])
    p.parallel_scale = scale
    p.show(screenshot=f"{output_path}.png")


def process_case(case, output_path):

    geom_vtp = f"{case}/postProcessing/surfacesVelocity/1000/geom_slice.vtp"
    vfield_vtp = f"{case}/postProcessing/surfacesVelocity/1000/s2.vtp"
    geom_mesh = pv.read(geom_vtp)
    vfield_mesh = pv.read(vfield_vtp)

    try:
        u, v, w = (vfield_mesh["U"][:,i] for i in range(3))
        geom = geom_mesh["U"][:,0]
    except (TypeError, KeyError) as e:
        print(f"Issue with {case} {e}")
        return

    clim=config["ux_uy_clim"]
    save_field(f"{output_path}_Ux", vfield_mesh, field=u, clim=clim)
    save_field(f"{output_path}_Uy", vfield_mesh, field=v, clim=clim)
    save_field(f"{output_path}_geom", geom_mesh, field=geom, clim=clim)

    clim=config["uz_clim"]
    save_field(f"{output_path}_Uz", vfield_mesh, field=w, clim=clim)

    im_Ux = Image.open(f'{output_path}_Ux.png', 'r')
    im_Uy = Image.open(f'{output_path}_Uy.png', 'r')
    im_Uz = Image.open(f'{output_path}_Uz.png', 'r')

    _, Ux, _ = im_Ux.split()
    _, Uy, _ = im_Uy.split()
    _, Uz, _ = im_Uz.split()
    im_combined = Image.merge("RGB", [Ux, Uy, Uz])
    im_combined.save(f'{output_path}.png')

    os.remove(f'{output_path}_Ux.png')
    os.remove(f'{output_path}_Uy.png')
    os.remove(f'{output_path}_Uz.png')


def main():

    with open("config.toml", "rb") as f:
        config = tomli.load(f)
    
    case_path = Path(config["case_path"])
    output_path = Path(config["output_path"])

    path = Path(case_path)
    Path.mkdir(output_path, exist_ok=True)
    cases = os.listdir(path)

    for case in cases:
        process_case(path/case, output_path/case)
        break

if __name__=='__main__':
    main()