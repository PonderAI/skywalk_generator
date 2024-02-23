# Code to convert the CFD data to images
import os
from pathlib import Path

import subprocess
import numpy as np
import multiprocessing as mp
from string import Template
import pyvista as pv
from PIL import Image
import glob
from matplotlib.colors import ListedColormap

def pv_headless():
    pv.OFFSCREEN = True
    os.environ['DISPLAY']=':99.0'
    commands = ['set -x',
                'Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &',
                'sleep 3',
                'set +x',
                'exec "$@"']
    for command in commands:
        subprocess.call(command,shell=True)

def save_field(output_path, name,mesh,field,clim,slice_j=2,output_folder=None,direction=None,empty=False,plane=False):

    scale = 650
    p = pv.Plotter(off_screen=True, window_size=[1024, 1024])
    vals = np.ones((256, 3))

    if empty:
        #cmap = ListedColormap(np.ones((256, 3))) # for building only
        vals[:, 0] = np.linspace(0, 1, 256)
        vals[:, 1] = np.linspace(0, 1, 256)
        vals[:, 2] = np.linspace(0, 1, 256)
        cmap = ListedColormap(vals)
        outfilename = f'{output_folder}/{name}_geom.png'
        p.add_mesh(plane, color="black")
    else:
        vals[:, 1] = np.linspace(0, 1, 256)
        cmap = ListedColormap(vals)
        outfilename = f'{output_path}.png'
    
    p.add_mesh(mesh, show_edges=False, scalars=field, lighting=False, show_scalar_bar=False, cmap=cmap, clim=clim)
    p.enable_parallel_projection()
    p.view_xy()
    p.set_background([1,1,1])
    p.parallel_scale = scale
    p.show(screenshot="cases/output/case_0_0.png")#

def make_output(case, output_path):
    # pv_headless()
    vtk_file = f'{case}/postProcessing/surfacesVelocity/1000/s2.vtp'
    mesh = pv.read(vtk_file)

    try:
        u, v, w = (mesh['U'][:,i] for i in range(3))
    except (TypeError, KeyError) as e:
        print(f"Issue with {case} {e}")
        return
    
    # if slice_j==2 and direction==0:
    #     stl_file = f'{input_folder}/constant/triSurface/building.stl'
    #     stl = pv.read(stl_file)
    #     # Add plane to ensure consistent scaling
    #     plane = pv.Plane(i_size=1.5e3, j_size=1.5e3)
    #     z = stl.points[:,2]
    #     clim=[0,100]
    #     save_field(f'{idx}',output_folder,direction,stl,z,clim,slice_j,empty=True,plane=plane)
    

    clim=[-6, 6]
    save_field(name=f'{case}_Ux', output_path=output_path/case, mesh=mesh, field=u, clim=clim)
    save_field(name=f'{case}_Uy', output_path=output_path/case, mesh=mesh, field=v, clim=clim)

    clim=[-2.0, 2.0]
    save_field(name=f'{case}_Uz', output_path=output_path/case, mesh=mesh, field=w, clim=clim)


    im_Ux = Image.open(f'{output_path/case}_Ux.png', 'r')
    im_Uy = Image.open(f'{output_path/case}_Uy.png', 'r')
    im_Uz = Image.open(f'{output_path/case}_Uz.png', 'r')

    _, Ux, _ = im_Ux.split()
    _, Uy, _ = im_Uy.split()
    _, Uz, _ = im_Uz.split()
    im_combined = Image.merge("RGB", [Ux, Uy, Uz])
    im_combined.save(f'{output_path/case}.png')

    os.remove(f'{output_path/case}_Ux.png')
    os.remove(f'{output_path/case}_Uy.png')
    os.remove(f'{output_path/case}_Uz.png')


def main():
    path = Path("cases")
    Path.mkdir(path/"output", exist_ok=True)
    output_path = path/"output"
    cases = os.listdir(path)

    for case in cases:
        make_output(path/case, output_path)
        break

if __name__=='__main__':
    main()