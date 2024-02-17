from flask import Flask, render_template, send_from_directory, Response, request, jsonify
from flask_cors import CORS
import subprocess
import signal
import os
import sys
import time
import psutil
from flask import Flask, render_template
import stashapi.log as log
from stashapi.stashapp import StashInterface

app = Flask(__name__, static_url_path='/static')
CORS(app)
CORS(app, resources={r"/graphql": {"origins": "http://localhost:9999"}})

# Store the subprocesses in a dictionary to manage them
running_processes = {}

# Store the count of script executions to terminate repeated requests
script_execution_count = {}

# Get the Flask server process ID
flask_server_pid = os.getpid()

# Mapping of script IDs to script paths
script_paths = {
    'export_performer_images': {
        'type': 'python',
        'path': './stashAssistant/python_scripts/Performer Image Export/stash_performer_image_export.py'
    },
    'gallery_scraper': {
        'type': 'node',
        'path': './stashAssistant/node_scripts/Performer Gallery Scraper/gallery_scraper.js'
    }
    # Add more scripts as needed
}

def execute_script(script_id):
    script_info = script_paths.get(script_id)
    if script_info:
        script_type = script_info['type']
        script_path = script_info['path']
        process = subprocess.Popen([script_type, script_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        return process
    else:
        raise ValueError('Invalid script ID')

def stream_output(process):
    for line in iter(process.stdout.readline, ''):
        yield 'data: {}\n\n'.format(line.strip())

@app.route('/')
def index():
    return render_template('index.html', app_name="Stash Assistant")

@app.route('/execute_script/<script_id>')
def execute_script_route(script_id):
    if script_id in script_paths:
        if script_id in script_execution_count:
            # Check if the script has already been executed once
            if script_execution_count[script_id] > 0:
                return jsonify({'error': 'Script already executed once'}), 400

        script_execution_count[script_id] = script_execution_count.get(script_id, 0) + 1

        try:
            process = execute_script(script_id)
            running_processes[script_id] = process
            return Response(stream_output(process), content_type='text/event-stream')
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Invalid script ID'}), 400

@app.route('/terminate_script/<script_type>', methods=['POST'])
def terminate_script(script_type):
    try:
        if script_type == 'python':
            # Iterate through all running processes except the Flask server process
            for proc in psutil.process_iter():
                try:
                    # Check if the process name contains 'python' and it's not the Flask server process
                    if 'python' in proc.name().lower() and proc.pid != flask_server_pid:
                        proc.terminate()  # Terminate the Python process
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            return jsonify({'message': 'Python scripts terminated successfully'}), 200
        elif script_type == 'node':
            # Iterate through all running processes
            for proc in psutil.process_iter():
                try:
                    # Check if the process name contains 'node'
                    if 'node' in proc.name().lower():
                        proc.terminate()  # Terminate the Node process
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            return jsonify({'message': 'Node scripts terminated successfully'}), 200
        else:
            return jsonify({'error': 'Invalid script type'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/featured')
def featured():
    return render_template('featured.html')
    
@app.route('/stash_editor')
def stash_editor():
    return render_template('stash_editor.html')

@app.route('/missing_scenes')
def missing_scenes():
    return render_template('missing_scenes.html')    
    
@app.route('/graphql')
def graphql():
    return render_template('graphql.html')
   
@app.route('/media_library')
def media_library():
    return render_template('media_library.html')

@app.route('/api/files/<path:directory>')
def get_files(directory):
    full_path = os.path.join('C:\\', directory)  # Adjust base directory as needed
    if os.path.isdir(full_path):
        files = os.listdir(full_path)
        file_data = []
        for file in files:
            file_path = os.path.join(full_path, file)
            file_info = {
                'name': file,
                'is_dir': os.path.isdir(file_path),
                'size': os.path.getsize(file_path),
            }
            file_data.append(file_info)
        return jsonify(file_data)
    else:
        return jsonify({'error': 'Directory not found'}), 404    

@app.route('/restart_stash_assistant', methods=['POST'])
def restart_stash_assistant():
    try:
        # Gracefully stop the server
        shutdown_server()
        # Allow time for the server to shut down
        time.sleep(1)
        # Restart the server
        python = sys.executable
        os.execl(python, python, *sys.argv)
    except Exception as e:
        return jsonify({'error': f'Failed to restart Stash Assistant: {str(e)}'}), 500

# Route to serve custom.css file
@app.route('/custom.css')
def serve_custom_css():
    return send_from_directory('C:\\Stash_Server\\', 'custom.css')

# Route to save changes to custom.css file
@app.route('/save', methods=['POST'])
def save_changes():
    content = request.json.get('content')
    try:
        with open('C:\\Stash_Server\\custom.css', 'w') as file:
            file.write(content)
        return jsonify({"message": "Changes saved successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stash_scene_details', methods=['GET', 'POST'])
def stash_scene_details():
    if request.method == 'POST':
        try:
            data = request.json
            old_path = data.get('oldPath')
            new_path = data.get('newPath')
            os.rename(old_path, new_path)
            return jsonify({'message': 'File renamed successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return render_template('stash_scene_details.html')

@app.route('/rename_file', methods=['POST'])
def rename_file():
    try:
        data = request.json
        old_path = data.get('oldPath')
        new_path = data.get('newPath')
        
        # Print out the old and new paths for debugging
        print("Old Path:", old_path)
        print("New Path:", new_path)
        
        os.rename(old_path, new_path)
        return jsonify({'message': 'File renamed successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/delete_file', methods=['POST'])
def delete_file():
    req_data = request.get_json()
    file_path = req_data['filePath']
    
    try:
        os.remove(file_path)
        return jsonify({'message': 'File deleted successfully.'})
    except Exception as e:
        return jsonify({'message': f'Error deleting file: {str(e)}'}), 500

@app.route('/stash_data')
def stash_data():
    return render_template('stash_data.html')


if __name__ == '__main__':
    app.run(debug=True)
