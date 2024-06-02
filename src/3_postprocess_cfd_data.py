# Code to convert the CFD data to images
import os
from pathlib import Path
import numpy as np
import pyvista as pv
from PIL import Image
from matplotlib.colors import ListedColormap

def save_field(output_path, mesh, field, clim, geom=False, negative=False):

    scale = 650
    p = pv.Plotter(off_screen=True, window_size=[1024, 1024])

    if geom:
        vals = np.ones((256, 3)) * (np.linspace(0, 1, 256)).reshape(256, 1)
        cmap = ListedColormap(vals)
        if negative:
            plane = pv.Plane(center=[0,0,clim[1]] ,i_size=1.5e3, j_size=1.5e3)
        else:
            plane = pv.Plane(center=[0,0,clim[0]] ,i_size=1.5e3, j_size=1.5e3)
        p.add_mesh(plane, color="black")
        

    else:
        vals = np.ones((256, 3))
        vals[:, 1] = np.linspace(0, 1, 256)
        cmap = ListedColormap(vals)
    
    p.add_mesh(mesh, show_edges=False, scalars=field, lighting=False, show_scalar_bar=False, cmap=cmap, clim=clim)
    p.enable_parallel_projection()
    p.view_xy(negative=negative)
    p.set_background([1,1,1])
    p.parallel_scale = scale
    p.show(screenshot=f"{output_path}.png")


def process_case(case, output_path):

    stl_file = case/f"constant/triSurface/buildings_0.stl"
    stl = pv.read(stl_file)

    z = stl.points[:,2]
    clim=[0,100]
    save_field(f"{output_path}_geom_top", mesh=stl, field=z, clim=clim, geom=True)
    save_field(f"{output_path}_geom_bottom", mesh=stl, field=z, clim=clim, geom=True, negative=True)

    vtk_file = f'{case}/postProcessing/surfacesVelocity/1000/s2.vtp'
    mesh = pv.read(vtk_file)

    try:
        u, v, w = (mesh['U'][:,i] for i in range(3))
    except (TypeError, KeyError) as e:
        print(f"Issue with {case} {e}")
        return

    clim=[-6, 6]
    save_field(f"{output_path}_Ux", mesh, field=u, clim=clim)
    save_field(f"{output_path}_Uy", mesh, field=v, clim=clim)

    clim=[-2.0, 2.0]
    save_field(f"{output_path}_Uz", mesh, field=w, clim=clim)


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
    path = Path("cases")
    Path.mkdir(path/"output", exist_ok=True)
    output_path = path/"output"
    cases = os.listdir(path)

    for case in cases:
        process_case(path/case, output_path/case)
        break

if __name__=='__main__':
    main()