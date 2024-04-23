

import os
import json
import shutil
from flask import Flask, request, render_template_string, jsonify, Response


import sys

# Initialize Flask application
app = Flask(__name__)


# Specify the app directory relative to the current file
app_dir = r'C:\Apache24\htdocs\personalProjects\StockTrader'
ignore_dirs = ['.git', 'node_modules', '__pycache__','.svelte-kit','OLD']  # Add or remove directories as needed
	
os.makedirs(app_dir, exist_ok=True)

@app.route('/editFile', methods=['POST'])
def editFile():
	"""
	Receives POST request with text and file path, saves the text to the specified file path within the app directory.
	"""
	text_data = request.form.get('text', '')
	file_path = request.form.get('file_path', '')

	if text_data and file_path:
		if file_path.startswith("/"):
			file_path = file_path[1:]
		full_file_path = os.path.join(app_dir, file_path)
		os.makedirs(os.path.dirname(full_file_path), exist_ok=True)
		text_data = text_data.replace('  ', '\t')
		with open(full_file_path, 'w') as file:
			file.write(text_data)
		return f"Text saved to {file_path}", 200
	return "No text or file path provided", 400

@app.route('/createFolder', methods=['POST'])
def createFolder():
	"""
	Receives POST request with the folder path and creates an empty folder at the specified path within the app directory.
	"""
	folder_path = request.form.get('folder_path', '')

	if folder_path:
		if folder_path.startswith("/"):
			folder_path = folder_path[1:]  # Remove leading slash if present

		full_folder_path = os.path.join(app_dir, folder_path)
		try:
			os.makedirs(full_folder_path, exist_ok=True)
			return f"Folder '{folder_path}' created successfully.", 200
		except Exception as e:
			return f"Failed to create folder: {str(e)}", 500
	return "No folder path provided", 400


@app.route('/rename', methods=['POST'])
def rename():
	"""
	Receives POST request to rename a file or folder.
	"""
	old_path = request.form.get('old_path')
	new_name = request.form.get('new_name')
	if not old_path or not new_name:
		return "Missing required data", 400
	full_old_path = os.path.join(app_dir, old_path)
	full_new_path = os.path.join(app_dir, os.path.dirname(old_path), new_name)
	if os.path.exists(full_old_path):
		try:
			os.rename(full_old_path, full_new_path)
			return f"{old_path} renamed to {new_name}", 200
		except Exception as e:
			return f"An error occurred: {e}", 500
	return "Path not found", 404

@app.route('/deleteFile', methods=['GET','DELETE'])
def delete_file():
	"""
	Deletes a specific file located at the given path within the app directory.
	"""
	file_path = request.args.get('file_path', '')
	full_file_path = os.path.join(app_dir, file_path)
	if os.path.exists(full_file_path):
		os.remove(full_file_path)
		return f"File {file_path} deleted successfully", 200
	return f"File {file_path} not found", 404

@app.route('/deleteFolder', methods=['GET','DELETE'])
def delete_folder():
	"""
	Deletes a folder and its contents located at the given path within the app directory.
	"""
	folder_path = request.args.get('folder_path', '')
	full_folder_path = os.path.join(app_dir, folder_path)
	try:
		shutil.rmtree(full_folder_path)
		return f"Folder {folder_path} deleted successfully", 200
	except FileNotFoundError:
		return "Folder not found", 404
	except PermissionError:
		return "Permission denied", 403
	except Exception as e:
		return f"An error occurred: {str(e)}", 500

@app.route('/listFiles', methods=['GET'])
def list_files():
	"""
	Lists all folders and files in the app directory, excluding specified directories.
	"""
	app_path = os.path.join(os.getcwd(), app_dir)
	folder_file_info = {'folders': [], 'files': []}
	for root, dirs, files in os.walk(app_path):
		dirs[:] = [d for d in dirs if d not in ignore_dirs]
		folder_file_info['folders'].append(root[len(app_path)+1:])
		for file in files:
			folder_file_info['files'].append(os.path.join(root[len(app_path)+1:], file))
	return jsonify(folder_file_info)



@app.route('/getFilesInFolder', methods=['GET'])
def get_files_in_folder():
	"""
	Returns all files within a specified folder directory along with their contents.
	"""
	folder_path = request.args.get('folder_path', '')
	if folder_path:
		app_path = os.path.join(os.getcwd(), app_dir, folder_path)
	else:
		app_path = os.path.join(os.getcwd(), app_dir)
	file_contents = {}
	if not os.path.isdir(app_path):
		return jsonify({'error': 'Folder not found'}), 404
	for root, dirs, files in os.walk(app_path):
		dirs[:] = [d for d in dirs if d not in ignore_dirs]  # Use global ignore_dirs
		for file in files:
			file_path = os.path.join(root, file)
			rel_file_path = os.path.relpath(file_path, app_path)
			try:
				with open(file_path, 'r') as f:
					content = f.read()
				file_contents[rel_file_path] = content
			except Exception as e:
				file_contents[rel_file_path] = f'Error reading file: {str(e)}'
	return jsonify(file_contents)


@app.route('/getSingleFile', methods=['GET'])
def get_single_file():
	"""
	Retrieves the content of a single file specified by the file path.
	"""
	file_path = request.args.get('file_path', '')
	full_file_path = os.path.join(app_dir, file_path)
	if os.path.exists(full_file_path):
		with open(full_file_path, 'r') as f:
			content = f.read()
		return jsonify({file_path: content})
	return jsonify({'error': f'File {file_path} not found'}), 404

@app.route('/form', methods=['GET'])
def form():
	
	"""
	Serves an HTML form for file operations.
	"""
	return render_template_string("""
	<!DOCTYPE html>
	<html>
	<body>
	<h2>Submit Text to Server or Rename File/Folder</h2>
	<h3>Edit File</h3>
	<form action="editFile" method="post">
		<label for="file_path">File Path:</label><br>
		<input type="text" id="file_path" name="file_path" required><br><br>
		<label for="text">Text:</label><br>
		<textarea id="text" name="text" rows="4" cols="50" required></textarea><br><br>
		<input type="submit" value="Submit">
	</form> 
	<h3>Rename File or Folder</h3>
	<form action="rename" method="post">
		<label for="old_path">Old Path:</label><br>
		<input type="text" id="old_path" name="old_path" required><br><br>
		<label for="new_name">New Name:</label><br>
		<input type="text" id="new_name" name="new_name" required><br><br>
		<input type="submit" value="Rename">
	</form>
	</body>
	</html>
	""")

# Use the previously defined global variable 'ignore_dirs'
@app.route('/menu', methods=['GET'])
def menu():
	"""
	Displays a navigation menu listing file operations and available files and folders.
	"""
	app_path = os.path.join(os.getcwd(), app_dir)
	html_content = "<h2>Menu</h2><ul>"
	html_content += "<li><a href='form'>Submit Text</a></li>"
	html_content += "<li><a href='listFiles'>List Files</a></li>"
	html_content += "<li><a href='getFilesInFolder'>View Files</a></li>"
	html_content += "</ul><h3>Files and Folders</h3><ul>"
	for root, dirs, files in os.walk(app_path):
		dirs[:] = [d for d in dirs if d not in ignore_dirs]  # Use the global 'ignore_dirs'
		if root != app_path:
			dir_path = os.path.relpath(root, app_path)
			html_content += f"<li><a href='getFilesInFolder?folder_path={dir_path}'>{dir_path}</a> - <a href='deleteFolder?folder_path={dir_path}'>(Delete)</a><ul>"
			for file in files:
				file_rel_path = os.path.join(dir_path, file)
				html_content += f"<li><a href='getSingleFile?file_path={file_rel_path}'>{file}</a> - <a href='deleteFile?file_path={file_rel_path}'>(Delete)</a></li>"
			html_content += "</ul></li>"
	for file in next(os.walk(app_path))[2]:
		html_content += f"<li><a href='getSingleFile?file_path={file}'>{file}</a> - <a href='deleteFile?file_path={file}'>(Delete)</a></li>"
	html_content += "</ul>"
	return html_content


@app.route('/robots.txt', methods=['GET'])
def robots_txt():
	"""
	Serves a hardcoded robots.txt to manage web crawler access.
	"""
	robots_content = "User-agent: *\nAllow: /"
	return Response(robots_content, mimetype='text/plain')

if __name__ == '__main__':
	app.run(debug=True, port=5000)
