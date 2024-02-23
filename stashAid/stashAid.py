from flask import Flask, render_template, send_from_directory, Response, request, jsonify, redirect, url_for
from flask_cors import CORS
import subprocess
import os
import sys
import time
import psutil
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import json
from apscheduler.jobstores.base import JobLookupError

# Initialize Flask app
app = Flask(__name__, static_url_path='/static')
CORS(app)
CORS(app, resources={r"/graphql": {"origins": "http://localhost:9999"}})

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = RotatingFileHandler('app.log', maxBytes=10000000, backupCount=3)

# Log Formatter
formatter = logging.Formatter('%(levelname)s - %(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Initialize APScheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Store the count of script executions to terminate repeated requests
script_execution_count = {}

# Get the Flask server process ID
flask_server_pid = os.getpid()

# List to store tasks
tasks = []

# Function to execute a script
def execute_script(script_id):
    script_info = script_paths.get(script_id)
    if script_info:
        script_type = script_info['type']
        script_path = script_info['path']
        process = subprocess.Popen([script_type, script_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        return process
    else:
        raise ValueError('Invalid script ID')

# Function to stream output from a process
def stream_output(process):
    for line in iter(process.stdout.readline, ''):
        yield 'data: {}\n\n'.format(line.strip())
        
# Schedule tasks with APScheduler
# Example task: execute the 'metadata_scan' script every day at 2:00 AM
scheduler.add_job(execute_script, 'cron', args=['metadata_scan'], hour=23, minute=30)

# Route to serve index.html template
@app.route('/')
def index():
    return render_template('index.html', app_name="Stash Assistant")

# Route to execute a script
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
            
            # Read output from the script and log it
            for line in iter(process.stdout.readline, b''):
                logger.info(line.strip())
            
            return Response(stream_output(process), content_type='text/event-stream')
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Invalid script ID'}), 400

# Route to terminate a script
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

# Route to serve featured.html template
@app.route('/featured')
def featured():
    return render_template('featured.html')

# Route to serve stash_editor.html template
@app.route('/stash_editor')
def stash_editor():
    return render_template('stash_editor.html')   

# Route to serve graphql.html template
@app.route('/graphql')
def graphql():
    return render_template('graphql.html')

# Route to serve media_library.html template
@app.route('/media_library')
def media_library():
    return render_template('media_library.html')

# Route to add a task
@app.route('/add_task', methods=['POST'])
def add_task():
    if request.method == 'POST':
        task_name = request.form['task_name']
        task_description = request.form['task_description']
        scheduled_time = request.form['scheduled_time']
        script_id = request.form['script_id']
        
        # Add the new task to the tasks list
        new_task = {'id': len(tasks) + 1, 'name': task_name, 'description': task_description, 'scheduled_time': scheduled_time, 'script_id': script_id}
        tasks.append(new_task)
        
        # Save the updated tasks to the JSON file
        save_tasks_to_json(tasks)
        
        return redirect(url_for('view_tasks'))


# Route to get files from a directory
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

# Route to restart the Stash Assistant
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

# Route to handle stash_scene_details.html
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

@app.route('/switch_move_files_flag', methods=['POST'])
def switch_move_files_flag():
    try:
        move_files_flag = request.json.get('moveFiles', False)  # Get the move files flag from the request
        logger.info(f"Move files flag updated to: {move_files_flag}")
        # Perform any other necessary actions based on the move files flag
        return jsonify({'message': 'Move files flag updated successfully'}), 200
    except Exception as e:
        logger.error(f"Error updating move files flag: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/rename_file', methods=['POST'])
def rename_file():
    try:
        data = request.json
        logger.info(f"Received data: {data}")
        
        old_path = Path(data.get('oldPath'))
        new_path = Path(data.get('newPath'))
        move_files = data.get('moveFiles', False)
        move_to_directory = data.get('moveToDirectory', None)
        
        logger.info(f"Old path: {old_path}, New path: {new_path}")
        logger.info(f"Move files flag: {move_files}, Move to directory: {move_to_directory}")

        # Ensure the new directory exists
        if move_files and move_to_directory:
            target_directory = Path(move_to_directory)
            # Check if the directory already exists
            if not os.path.exists(target_directory):
                os.makedirs(target_directory, exist_ok=True)
                logger.info(f"Target directory created: {target_directory}")
            else:
                logger.info(f"Target directory already exists: {target_directory}")
        
        # Rename (move) the file to the new path
        old_path.rename(new_path)
        logger.info(f"File renamed from {old_path} to {new_path}")

        # Move the file to a new directory if requested
        if move_files and move_to_directory:
            final_path = target_directory / new_path.name
            # Move the file to the final path
            new_path.rename(final_path)
            logger.info(f"File moved to {final_path}")
        
        return jsonify({'message': 'File renamed successfully'})
    except Exception as e:
        logger.error(f"Error renaming/moving file: {str(e)}")
        return jsonify({'error': str(e)}), 500


# Route to handle file deletion
@app.route('/delete_file', methods=['POST'])
def delete_file():
    req_data = request.get_json()
    file_path = req_data['filePath']
    
    try:
        os.remove(file_path)
        return jsonify({'message': 'File deleted successfully.'})
    except Exception as e:
        return jsonify({'message': f'Error deleting file: {str(e)}'}), 500

# Route to serve stash_data.html template
@app.route('/stash_data')
def stash_data():
    return render_template('stash_data.html')

# Route to serve admin.html template
@app.route('/admin')
def admin():
    return render_template('admin.html')

# Route to view logs
@app.route('/logs')
def view_logs():
    level = request.args.get('level', '').upper()
    query = request.args.get('query', '').lower()
    
    logs = []
    with open('app.log', 'r') as log_file:
        for line in log_file:
            if (not level or level in line) and (not query or query in line.lower()):
                logs.append(line)
    
    return render_template('logs.html', logs=logs)


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

@app.errorhandler(404)
def page_not_found(error):
    return jsonify({'error': 'Page not found'}), 404

# Mapping of script IDs to script paths
script_paths = {}

# Function to recursively search for scripts in the specified directories
def find_scripts(directory):
    for root, dirs, files in os.walk(directory):
        # Check if the current directory is one of the allowed script directories
        if (root.startswith('./node-scripts') or root.startswith('./python-scripts')) and 'node_modules' not in root:
            for file in files:
                if file.endswith('.py') or file.endswith('.js'):
                    script_id = file.split('.')[0]  # Extract script ID from filename
                    script_type = 'python' if file.endswith('.py') else 'node'
                    script_path = os.path.join(root, file)
                    script_paths[script_id] = {'type': script_type, 'path': script_path}

# Specify the directories containing the scripts
script_directories = ['./python-scripts', './node-scripts']

# Populate script_paths dictionary by searching for scripts in the specified directories
for directory in script_directories:
    find_scripts(directory)

# Route to serve tasks.html template
@app.route('/view_tasks')
def view_tasks():
    # Filter script_paths to include only scripts associated with current tasks
    task_script_ids = {task['script_id'] for task in tasks}
    filtered_script_paths = {script_id: script_info for script_id, script_info in script_paths.items() if script_id in task_script_ids}
    
    return render_template('tasks.html', tasks=tasks, script_paths=script_paths)



# Populate script_paths dictionary by searching for scripts in the specified directories
script_paths = {}
for directory in script_directories:
    find_scripts(directory)
    
# Route to delete a task
@app.route('/delete_task/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    global tasks
    try:
        scheduler.remove_job(str(task_id))
    except JobLookupError:
        pass  # Job not found in scheduler
    tasks = [task for task in tasks if task['id'] != task_id]
    save_tasks_to_json(tasks)
    return jsonify({'message': 'Task deleted successfully'}), 200

# JSON file path for storing scheduled tasks
TASKS_JSON_FILE = 'tasks.json'

# Define a function to save tasks to JSON
def save_tasks_to_json(tasks):
    with open(TASKS_JSON_FILE, 'w') as json_file:
        json.dump(tasks, json_file, indent=4)

# Define a function to load tasks from JSON
def load_tasks_from_json():
    try:
        with open(TASKS_JSON_FILE, 'r') as json_file:
            # Load tasks from JSON file if it's not empty
            return json.load(json_file)
    except FileNotFoundError:
        # Return an empty list if the file doesn't exist yet
        return []
    except json.JSONDecodeError:
        # Handle the case when the file contains invalid JSON data
        logger.error('Error decoding JSON data from tasks.json')
        return []

# Call the load function on Flask app startup
tasks = load_tasks_from_json()

# Schedule loaded tasks with APScheduler
for task in tasks:
    try:
        scheduled_datetime = datetime.fromisoformat(task['scheduled_time'])
        scheduled_hour = scheduled_datetime.hour
        scheduled_minute = scheduled_datetime.minute
        scheduler.add_job(
            execute_script,
            'cron',
            args=[task['script_id']],
            id=str(task['id']),
            name=task['name'],
            hour=scheduled_hour,
            minute=scheduled_minute
        )
    except Exception as e:
        logger.error(f"Failed to schedule task {task['id']}: {str(e)}")

import os
from flask import jsonify, request

# Route to handle file moves
@app.route('/move_file', methods=['POST'])
def move_file():
    data = request.json
    old_path = data.get('oldPath')
    new_path = data.get('newPath')

    try:
        # Ensure the destination directory exists
        if not os.path.exists(new_path):
            os.makedirs(new_path)

        # Extract filename from the old path
        filename = os.path.basename(old_path)

        # Construct the new file path
        new_file_path = os.path.join(new_path, filename)

        # Move the file to the new path
        os.replace(old_path, new_file_path)

        message = f"File '{filename}' moved successfully to {new_path}"
        return jsonify({'message': message}), 200
    except Exception as e:
        error_message = str(e)
        return jsonify({'error': error_message}), 500


# Route to handle directory creation requests
@app.route('/create_directory', methods=['POST'])
def create_directory():
    try:
        directory = request.json.get('directory')
        # Check if the directory already exists
        if os.path.exists(directory):
            logger.info(f"Directory already exists: {directory}")
            return jsonify({'message': 'Directory already exists'}), 200
        # Create the directory
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Directory created successfully: {directory}")
        return jsonify({'message': 'Directory created successfully'}), 200
    except Exception as e:
        logger.error(f"Error creating directory: {str(e)}")
        return jsonify({'error': str(e)}), 500


# Start Flask app
if __name__ == '__main__':
    app.run(debug=True)