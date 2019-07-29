from django.conf import settings
import subprocess
import platform
import os
import stl

import numpy as np
from vispy import app, gloo, geometry, io
from vispy.geometry import create_sphere
from vispy.scene import visuals, cameras
from vispy.visuals.transforms import (STTransform, MatrixTransform,
                                      ChainTransform)

import trimesh
import vispy.scene

# This file contains various helper functions needed for the app.
# These helpers do not fit perfectly into the django structure of models,
# views and controllers so we have created a special place for them.

class Canvas(vispy.scene.SceneCanvas):
    def __init__(self, model_path, x):
        vispy.scene.SceneCanvas.__init__(self, dpi=100, bgcolor='w')
        self.unfreeze()
        self.meshes = []
        view = self.central_widget.add_view()
        mesh = trimesh.load(model_path)
        mdata = geometry.MeshData(mesh.vertices, mesh.faces)
        self.meshes.append(visuals.Mesh(meshdata=mdata, shading='smooth', parent=view.scene))
        view.camera = vispy.scene.TurntableCamera()
        view.camera.fov = 30
        view.camera.distance = x * 7
        self.freeze()

def create_thumbnail(model_path, x):
    size = '200'
    name = strip_extension(model_path) + '.png'
    output_path = os.path.join(settings.THUMBS_ROOT, get_file_name(name))
    win = Canvas(model_path, x)
    img = win.render()
    io.write_png(output_path, img)
    win.close()

def delete_thumbnail(file_path):
	name = strip_extension(file_path) + '.png'
	png_path = os.path.join(settings.THUMBS_ROOT, get_file_name(name))
	if os.path.exists(png_path):
		os.remove(png_path)

def find_mins_maxs(obj):
    minx = maxx = miny = maxy = minz = maxz = None
    for p in obj.vertices:
        # p contains (x, y, z)
        if minx is None:
            minx = p[stl.Dimension.X]
            maxx = p[stl.Dimension.X]
            miny = p[stl.Dimension.Y]
            maxy = p[stl.Dimension.Y]
            minz = p[stl.Dimension.Z]
            maxz = p[stl.Dimension.Z]
        else:
            maxx = max(p[stl.Dimension.X], maxx)
            minx = min(p[stl.Dimension.X], minx)
            maxy = max(p[stl.Dimension.Y], maxy)
            miny = min(p[stl.Dimension.Y], miny)
            maxz = max(p[stl.Dimension.Z], maxz)
            minz = min(p[stl.Dimension.Z], minz)
    return minx, maxx, miny, maxy, minz, maxz

def get_dims(file_path):
    model = trimesh.load(file_path)
    minx, maxx, miny, maxy, minz, maxz = find_mins_maxs(model)
    x_dims = maxx - minx
    y_dims = maxy - miny
    z_dims = maxz - minz
    return round(x_dims, 2), round(y_dims, 2), round(z_dims, 2)

def delete_file(file_path):
	os.remove(file_path)

def get_file_name(path):
    return path.split("/")[-1]

def get_extension(file_path):
    return file_path.split('.')[1]

def strip_extension(file_path):
    return file_path.split('.')[0] if file_path else ''