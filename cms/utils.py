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

class Canvas(vispy.scene.SceneCanvas):
    def __init__(self, stl_path):
        vispy.scene.SceneCanvas.__init__(self, keys='interactive', size=(540, 360), bgcolor='w')
        self.unfreeze()
        self.meshes = []
        view = self.central_widget.add_view()
        view.camera = 'turntable'
        view.camera.fov = 50
        view.camera.distance = 25
        mesh = trimesh.load(stl_path)
        mdata = geometry.MeshData(mesh.vertices, mesh.faces)
        self.meshes.append(visuals.Mesh(meshdata=mdata, shading='flat', parent=view.scene))
        self.freeze()

def create_thumbnail(stl_path, size='200'):
	name = strip_extension(stl_path) + '.png'
	output_path = os.path.join(settings.THUMBS_ROOT, get_file_name(name))
	win = Canvas(stl_path)
	img = win.render()
	io.write_png(output_path, img)

def delete_thumbnail(file_path):
	name = strip_extension(file_path) + '.png'
	png_path = os.path.join(settings.THUMBS_ROOT, get_file_name(name))
	if os.path.exists(png_path):
		os.remove(png_path)

def delete_file(file_path):
	os.remove(file_path)

def get_file_name(path):
    return path.split("/")[-1]

def get_extension(file_path):
    return file_path.split('.')[1]

def strip_extension(file_path):
    return file_path.split('.')[0] if file_path else ''