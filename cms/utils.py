import subprocess
import platform
import ntpath
import os
# This file contains various helper functions needed for the app.
# These helpers do not fit perfectly into the django structure of models,
# views and controllers so we have created a special place for them.

# Functions defined here and their uses:

# 1. create_thumbnail(stl_path, filename) -> This function uses a command line utility
# 	 called 'stl-thumb' to generate PNG files from STL files. The PNGs are used in templates
# 	 to offer a preview of the STL file. Install https://github.com/unlimitedbacon/stl-thumb/
# 	 is a requirement for this function

def create_thumbnail(stl_path, output_path):
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

def delete_files(*args):
	# kwargs is a dict of the keyword args passed to the function
	for path in args:
		try:
			os.remove(path)
		except FileNotFoundError:
			print('Failed to delete file.')

def extract_file_name(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def get_extension(file_path):
    return file_path.split('.')[1]

def remove_extension(file_path):
    return file_path.split('.')[0] if file_path else ''