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
# These do not fit perfectly into the django structure of MVC.

def create_thumbnail(path, model, up="z"):
    canvas = vispy.scene.SceneCanvas(bgcolor='white')
    canvas.unfreeze()
    canvas.view = canvas.central_widget.add_view()
    mesh = vispy.scene.visuals.Mesh(vertices=model.vertices, shading='flat', faces=model.faces)
    canvas.view.add(mesh)
    if path.endswith(".obj"):
        up = "y"
    canvas.view.camera = vispy.scene.TurntableCamera(up=up, fov=30)
    canvas.view.camera.depth_value = 1
    img = canvas.render()
    img_name = change_ext(path, '.png')
    img_path = os.path.join(settings.THUMBS_ROOT, get_file_name(img_name))
    io.write_png(img_path, img)
    canvas.close()

def delete_thumbnail(path):
	img_name = change_ext(path, '.png')
	img_path = os.path.join(settings.THUMBS_ROOT, get_file_name(img_name))
	if os.path.exists(img_path):
		os.remove(img_path)

def get_dimensions(model):
    minx, maxx, miny, maxy, minz, maxz = model.bounds.T.flatten()
    x = maxx - minx
    y = maxy - miny
    z = maxz - minz
    x_y_z = [str(round(x, 2)), str(round(y, 2)), str(round(z, 2))]
    dimensions = ', '.join(x_y_z)
    return dimensions

def delete_if_exists(self, entry_type):
    if entry_type.objects.filter(entry=self).exists():
        entry_type.objects.get(entry=self).delete()

def add_file(self, entry_type, file):
    entry_type.objects.create(entry=self, document=file).save()

def get_object(self, entry_type):
    return entry_type.objects.get(entry=self)

def delete_file(path):
	os.remove(path)

def change_ext(path, ext):
    return strip_ext(path) + ext

def get_file_name(path):
    return path.split("/")[-1]

def get_ext(path):
    return path.split('.')[-1]

def strip_ext(path):
    return path.split('.')[0] if path else ''