from django.conf import settings
import subprocess
import platform
import os

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

def create_thumbnail(file_path, model, z):
    name = strip_ext(file_path) + '.png'
    output_path = os.path.join(settings.THUMBS_ROOT, get_file_name(name))
    canvas = vispy.scene.SceneCanvas(bgcolor='white')
    canvas.unfreeze()
    canvas.view = canvas.central_widget.add_view()
    mesh = vispy.scene.visuals.Mesh(vertices=model.vertices, shading='smooth', faces=model.faces)
    canvas.view.add(mesh)
    canvas.view.camera = vispy.scene.TurntableCamera()
    canvas.view.camera = vispy.scene.TurntableCamera()
    canvas.view.camera.fov = 30
    canvas.view.camera.distance = (z * 3.5)
    img = canvas.render()
    io.write_png(output_path, img)

def delete_thumbnail(file_path):
	name = strip_ext(file_path) + '.png'
	png_path = os.path.join(settings.THUMBS_ROOT, get_file_name(name))
	if os.path.exists(png_path):
		os.remove(png_path)

def get_dims(model):
    minx, maxx, miny, maxy, minz, maxz = find_mins_maxs(model)
    x_dims = maxx - minx
    y_dims = maxy - miny
    z_dims = maxz - minz
    return round(x_dims, 2), round(y_dims, 2), round(z_dims, 2)

def find_mins_maxs(obj):
    minx = maxx = miny = maxy = minz = maxz = None
    for p in obj.vertices:
        if minx is None:
            minx = p[0]
            maxx = p[0]
            miny = p[1]
            maxy = p[1]
            minz = p[2]
            maxz = p[2]
        else:
            maxx = max(p[0], maxx)
            minx = min(p[0], minx)
            maxy = max(p[1], maxy)
            miny = min(p[1], miny)
            maxz = max(p[2], maxz)
            minz = min(p[2], minz)
    return minx, maxx, miny, maxy, minz, maxz

def delete_file(file_path):
	os.remove(file_path)

def get_file_name(path):
    return path.split("/")[-1]

def get_ext(file_path):
    return file_path.split('.')[1]

def strip_ext(file_path):
    return file_path.split('.')[0] if file_path else ''