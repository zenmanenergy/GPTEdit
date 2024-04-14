import os
import json
import shutil
from flask import Flask, request, render_template_string, jsonify, Response

# Initialize Flask application
app = Flask(__name__)

# Specify the app directory relative to the current file
app_dir = 'app'
os.makedirs(app_dir, exist_ok=True)



@app.route('/', methods=['GET', 'POST'])
def main_router():
	"""
	Main router that checks the action parameter to determine the requested operation.
	"""
	action = request.args.get('action', '')
	
	if request.method == 'POST':
		if action == 'editFile':
			return editFile()
		elif action == 'rename':
			return rename()
	elif request.method == 'GET':
		if action == 'form':
			return form()
		elif action == 'menu':
			return menu()
		elif action == 'deleteFile':
			file_path = request.args.get('file_path', '')
			return deleteFile(file_path)
		elif action == 'deleteFolder':
			folder_path = request.args.get('folder_path', '')
			return deleteFolder(folder_path)
		elif action == 'listFiles':
			return listFiles()
		elif action == 'getFilesInFolder':
			folder_path = request.args.get('folder_path', '')
			return getFilesInFolder(folder_path)
		elif action == 'getSingleFile':
			file_path = request.args.get('file_path', '')
			return getSingleFile(file_path)
		elif action == 'robots.txt':
			return robots_txt()

	return "Invalid action or method.", 400

def editFile():
	"""
	Endpoint to receive a POST request with text and file path,
	save the text to the specified file path within the app directory.
	"""
	# Retrieve text and file path from the form
	text_data = request.form.get('text', '')
	file_path = request.form.get('file_path', '')

	if text_data and file_path:
		# Remove leading "/" if present in the file path  
		if file_path.startswith("/"):
			file_path = file_path[1:]

		# Define the full file path where the text will be saved
		full_file_path = os.path.join(app_dir, file_path)

		# Ensure the directory structure exists for the file path
		os.makedirs(os.path.dirname(full_file_path), exist_ok=True)

		# Replace two spaces with a tab character in the text data
		text_data = text_data.replace('  ', '\t')

		# Save the text data to the specified file path
		with open(full_file_path, 'w') as file:
			file.write(text_data)
		
		return f"Text received and saved to {file_path}", 200
	
	return "No text or file path found", 400

def form():
	"""
	Serves an HTML form allowing users to submit text to edit a file and provide details to rename a file or folder.
	"""
	return render_template_string("""
	<!DOCTYPE html>
	<html>
	<body>
	
	<h2>Submit Text to Server or Rename File/Folder</h2>
	
	<h3>Edit File</h3>
	<form action="?action=editFile" method="post">
	  <label for="file_path">File Path:</label><br>
	  <input type="text" id="file_path" name="file_path" required><br><br>
	  <label for="text">Text:</label><br>
	  <textarea id="text" name="text" rows="4" cols="50" required></textarea><br><br>
	  <input type="submit" value="Submit">
	</form> 

	<h3>Rename File or Folder</h3>
	<form action="?action=rename" method="post">
	  <label for="old_path">Old Path:</label><br>
	  <input type="text" id="old_path" name="old_path" required><br><br>
	  <label for="new_name">New Name:</label><br>
	  <input type="text" id="new_name" name="new_name" required><br><br>
	  <input type="submit" value="Rename">
	</form>
	
	</body>
	</html>
	""")


def menu():
	"""
	Displays a navigation menu listing file operations and available files and folders.
	"""
	# Define the path to the app directory
	app_path = os.path.join(os.getcwd(), app_dir)

	# Initialize an HTML content string for the menu
	html_content = "<h2>Menu</h2><ul>"
	html_content += "<li><a href='?action=form'>Submit Text</a></li>"
	html_content += "<li><a href='?action=listFiles'>List Files</a></li>"
	html_content += "<li><a href='?action=getFilesInFolder'>View Files</a></li>"
	html_content += "</ul><h3>Files</h3><ul>"

	# List files and directories in the app directory
	for root, dirs, files in os.walk(app_path):
		for directory in dirs:
			dir_path = os.path.join(root, directory)
			html_content += f"<li><a href='?action=menu/{os.path.relpath(dir_path, app_path)}'>{directory}</a> - <a href='?action=deleteFolder/{os.path.relpath(dir_path, app_path)}'>(Delete)</a></li>"
		for file in files:
			file_path = os.path.join(root, file)
			html_content += f"<li><a href='?action=getSingleFile/{os.path.relpath(file_path, app_path)}'>{file}</a> - <a href='?action=deleteFile/{os.path.relpath(file_path, app_path)}'>(Delete)</a></li>"
	html_content += "</ul>"
	return html_content

def deleteFile(file_path):
	"""
	Endpoint to delete a specific file located at the given path within the app directory.
	"""
	# Define the full file path
	full_file_path = os.path.join(app_dir, file_path)

	# Check if the file exists and delete it
	if os.path.exists(full_file_path):
		os.remove(full_file_path)
		return f"File {file_path} deleted successfully", 200
	else:
		return {'error': f'File {file_path} not found'}, 404

def deleteFolder(folder_path):
	"""
	Endpoint to delete a folder and its contents located at the given path within the app directory.
	Handles errors if the folder is not found or other exceptions occur.
	"""
	# Define the full folder path
	full_folder_path = os.path.join(app_dir, folder_path)

	try:
		shutil.rmtree(full_folder_path)
		return f"Folder {folder_path} deleted successfully", 200
	except FileNotFoundError:
		return {'error': f'Folder {folder_path} not found'}, 404
	except Exception as e:
		return {'error': f'An error occurred: {e}'}, 500

def listFiles():
	"""
	Lists all folders and files in the app directory.
	Outputs the list in JSON format.
	"""
	# Define the path to the app directory
	app_path = os.path.join(os.getcwd(), app_dir)

	# Initialize a dictionary to store the folder and file information
	folder_file_info = {'folders': [], 'files': []}

	# Traverse the app directory and record all directories and files
	for root, dirs, files in os.walk(app_path):
		folder_file_info['folders'].append(root[len(app_path)+1:])
		for file in files:
			folder_file_info['files'].append(os.path.join(root[len(app_path)+1:], file))

	# Convert the dictionary to JSON format and return
	json_packet = json.dumps(folder_file_info)
	return json_packet

def getFilesInFolder(folder_path):
	"""
	Endpoint that returns a JSON containing all files within a specified folder directory along with their contents.
	"""
	# Define the path to the specified folder within the app directory
	app_path = os.path.join(os.getcwd(), app_dir, folder_path)

	# Initialize a dictionary to store the file paths and contents
	file_contents = {}

	# Check if the specified path is actually a directory
	if not os.path.isdir(app_path):
		return jsonify({'error': 'Folder not found'}), 404

	# Traverse the specified folder directory and add file contents to the dictionary
	for root, dirs, files in os.walk(app_path):
		for file in files:
			file_path = os.path.join(root[len(app_path)+1:], file)
			with open(os.path.join(app_path, file_path), 'r') as f:
				content = f.read()
			file_contents[file_path] = content

	# Convert the dictionary to JSON format and return
	json_packet = json.dumps(file_contents)
	return json_packet


def getSingleFile(file_path):
	"""
	Retrieves the content of a single file specified by the file path.
	Returns the content in JSON format. Handles file not found errors.
	"""
	# Define the path to the app directory
	app_path = os.path.join(os.getcwd(), app_dir)

	# Construct the full file path
	full_file_path = os.path.join(app_path, file_path)

	# Check if the file exists and read its contents
	if os.path.exists(full_file_path):
		with open(full_file_path, 'r') as f:
			content = f.read()
		file_info = {file_path: content}
		json_packet = json.dumps(file_info)
		return json_packet
	else:
		return {'error': f'File {file_path} not found'}

def rename_file():
	"""
	Endpoint to rename a specific file. Expects JSON data with 'old_file_path' and 'new_file_name'.
	Returns a success message or an error if the file cannot be found or renamed.
	"""
	data = request.get_json()
	old_file_path = data.get('old_file_path', '')
	new_file_name = data.get('new_file_name', '')

	if not old_file_path or not new_file_name:
		return jsonify({'error': 'Missing file path or new file name'}), 400

	# Define the full old and new file paths
	old_full_path = os.path.join(app_dir, old_file_path)
	new_full_path = os.path.join(app_dir, os.path.dirname(old_file_path), new_file_name)

	if os.path.exists(old_full_path):
		try:
			os.rename(old_full_path, new_full_path)
			return jsonify({'message': f'File renamed to {new_file_name}'}), 200
		except Exception as e:
			return jsonify({'error': f'An error occurred: {e}'}), 500
	else:
		return jsonify({'error': 'File not found'}), 404
	
def rename():
	"""
	Endpoint to rename a specific file or folder based on its type (determined by checking if it's a file or directory).
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
	else:
		return "Path not found", 404

def robots_txt():
	"""
	Serves a hardcoded robots.txt to manage web crawler access.
	"""
	robots_content = "User-agent: *\nAllow: /"
	return Response(robots_content, mimetype='text/plain')

if __name__ == '__main__':
	app.run(debug=True, port=5000)
