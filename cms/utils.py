from django.conf import settings
from .utils import *
import subprocess
import platform
import os
# This file contains various helper functions needed for the app.
# These helpers do not fit perfectly into the django structure of models,
# views and controllers so we have created a special place for them.

# Functions defined here and their uses:

# 1. create_thumbnail(stl_path, filename) -> This function uses a command line utility
# 	 called 'stl-thumb' to generate PNG files from STL files. The PNGs are used in templates
# 	 to offer a preview of the STL file. Install https://github.com/unlimitedbacon/stl-thumb/
# 	 is a requirement for this function

def create_thumbnail(stl_path):
	name = strip_extension(stl_path) + '.png'
	output_path = os.path.join(settings.THUMBS_ROOT, get_file_name(name))

	stl_thumb_exe = 'C:\\Program Files\\stl-thumb\\stl-thumb.exe'  # Default is windows
	if platform.system() == 'Linux':
		stl_thumb_exe = 'stl-thumb'

	size = '200'  # 200 x 200 pixel
	command = [stl_thumb_exe, stl_path, output_path, '-s', size]
	process = subprocess.run(command)
	if process.returncode == 0:
		print('Created Thumbnail at {}'.format(output_path))

def delete_thumbnail(file_path):
	name = strip_extension(file_path) + '.png'
	png_path = os.path.join(settings.THUMBS_ROOT, get_file_name(name))
	os.remove(png_path)

def get_file_name(path):
    return path.split("/")[-1]

def get_extension(file_path):
    return file_path.split('.')[1]

def strip_extension(file_path):
    return file_path.split('.')[0] if file_path else ''