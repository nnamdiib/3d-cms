import subprocess
import os
import platform
# This file contains various helper functions needed for the app.
# These helpers do not fit perfectly into the django structure of models,
# views and controllers so we have created a special place for them.

# Functions defined here and their uses:

# 1. create_thumbnail(stl_path, filename) -> This function uses a command line utility
# 	 called 'stl-thumb' to generate PNG files from STL files. The PNGs are used in templates
# 	 to offer a preview of the STL file. Install https://github.com/unlimitedbacon/stl-thumb/
# 	 is a requirement for this function

def create_thumbnail_windows(stl_path, output_path):
	stl_thumb_exe = 'C:\\Program Files\\stl-thumb\\stl-thumb.exe'  # Default is windows
	if platform.system() == 'Linux':
		# We are on a linux machine
		stl_thumb_exe = 'stl-thumb'

	size = '200'  # Specify a 200 x 200 pixel PNG
	command = [stl_thumb_exe, stl_path, output_path, '-s', size]
	print(command)
	process = subprocess.run(command)
	if process.returncode == 0:
		print('Created Thumbnail at {}'.format(output_path))

def create_thumbnail_linux(stl_path, output_path):
	os.environ["PYOPENGL_PLATFORM"] = "egl"
	import numpy as np
	import trimesh
	import pyrender
	import matplotlib.pyplot as plt

	model_data = trimesh.load(stl_path)
	mesh = pyrender.Mesh.from_trimesh(model_data)
	scene = pyrender.Scene()
	scene.add(mesh)

	# Set up the camera -- z-axis away from the scene, x-axis right, y-axis up
	camera = pyrender.PerspectiveCamera(yfov=np.pi / 3.0)
	s = np.sqrt(2)/2

	camera_pose = np.array([
       [0.0, -s,   s,   0.3],
       [1.0,  0.0, 0.0, 0.0],
       [0.0,  s,   s,   0.35],
       [0.0,  0.0, 0.0, 1.0],
    ])

	scene.add(camera, pose=camera_pose)

	# Set up the light -- a single spot light in the same spot as the camera
	light = pyrender.SpotLight(color=np.ones(3), intensity=3.0,
                               innerConeAngle=np.pi/16.0)
	
	scene.add(light, pose=camera_pose)

	# Render the scene
	r = pyrender.OffscreenRenderer(200, 200)
	color, depth = r.render(scene)

	# Show the images
	plt.figure()
	plt.subplot(1,1,1)
	plt.axis('off')
	plt.imshow(color)
	plt.savefig(output_path)


create_thumbnail = create_thumbnail_linux if platform.system() == 'Linux' else create_thumbnail_windows
