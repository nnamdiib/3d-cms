from django.conf import settings
import subprocess
import platform
import os

from stl import mesh
from mpl_toolkits import mplot3d
from matplotlib import pyplot

# This file contains various helper functions needed for the app.
# These helpers do not fit perfectly into the django structure of models,
# views and controllers so we have created a special place for them.

def create_thumbnail(stl_path):
	name = strip_extension(stl_path) + '.png'
	output_path = os.path.join(settings.THUMBS_ROOT, get_file_name(name))
	figure = pyplot.figure()
	axes = mplot3d.Axes3D(figure)

	your_mesh = mesh.Mesh.from_file(stl_path)
	axes.add_collection3d(mplot3d.art3d.Poly3DCollection(your_mesh.vectors))

	scale = your_mesh.points.flatten(-1)
	axes.auto_scale_xyz(scale, scale, scale)
	pyplot.axis('off')
	pyplot.savefig(output_path, dpi=30)

def delete_thumbnail(file_path):
	name = strip_extension(file_path) + '.png'
	png_path = os.path.join(settings.THUMBS_ROOT, get_file_name(name))
	os.remove(png_path)

def delete_file(file_path):
	os.remove(file_path)

def get_file_name(path):
    return path.split("/")[-1]

def get_extension(file_path):
    return file_path.split('.')[1]

def strip_extension(file_path):
    return file_path.split('.')[0] if file_path else ''