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

def create_thumbnail(file_path):
    name = strip_ext(file_path) + '.png'
    img_name = os.path.join(settings.THUMBS_ROOT, get_file_name(name))
    model = trimesh.load_mesh(file_path)
    canvas = vispy.scene.SceneCanvas(bgcolor='white')
    canvas.unfreeze()
    canvas.view = canvas.central_widget.add_view()
    mesh = vispy.scene.visuals.Mesh(vertices=model.vertices, shading='flat', faces=model.faces)
    canvas.view.add(mesh)
    canvas.view.camera = vispy.scene.TurntableCamera()
    canvas.view.camera.fov = 30
    canvas.view.camera.distance = 0
    img = canvas.render()
    io.write_png(img_name, img)
    canvas.close()

def delete_thumbnail(file_path):
	name = strip_ext(file_path) + '.png'
	png_path = os.path.join(settings.THUMBS_ROOT, get_file_name(name))
	if os.path.exists(png_path):
		os.remove(png_path)

def delete_file(file_path):
	os.remove(file_path)

def get_file_name(path):
    return path.split("/")[-1]

def get_ext(file_path):
    return file_path.split('.')[1]

def strip_ext(file_path):
    return file_path.split('.')[0] if file_path else ''