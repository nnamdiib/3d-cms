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

def create_thumbnail(path, model):
    canvas = vispy.scene.SceneCanvas(bgcolor='white')
    canvas.unfreeze()
    canvas.view = canvas.central_widget.add_view()
    mesh = vispy.scene.visuals.Mesh(vertices=model.vertices, shading='flat', faces=model.faces)
    canvas.view.add(mesh)
    canvas.view.camera = vispy.scene.TurntableCamera()
    canvas.view.camera.depth_value = 1
    canvas.view.camera.fov = 30
    canvas.view.camera.distance = 0
    img = canvas.render()
    img_name = strip_ext(path) + '.png'
    img_path = os.path.join(settings.THUMBS_ROOT, get_file_name(img_name))
    io.write_png(img_path, img)
    canvas.close()

def delete_thumbnail(path):
	img_name = strip_ext(path) + '.png'
	img_path = os.path.join(settings.THUMBS_ROOT, get_file_name(img_name))
	if os.path.exists(img_path):
		os.remove(img_path)

def get_dimensions(model):
    minx, maxx, miny, maxy, minz, maxz = model.bounds.T.flatten()
    x = maxx - minx
    y = maxy - miny
    z = maxz - minz
    dimensions = [str(round(x, 2)), str(round(y, 2)), str(round(z, 2))]
    return dimensions

def delete_file(path):
	os.remove(path)

def get_file_name(path):
    return path.split("/")[-1]

def get_ext(path):
    return path.split('.')[-1]

def strip_ext(path):
    return path.split('.')[0] if path else ''