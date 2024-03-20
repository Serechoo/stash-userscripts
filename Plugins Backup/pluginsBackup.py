import shutil
import os
import datetime
import stashapi.log as log

def backup_plugins():
    source_dir = os.path.dirname(os.path.abspath(__file__))  # Get the absolute path of the script's directory
    plugins_dir = os.path.basename(source_dir)
    backup_parent_dir = os.path.abspath(os.path.join(source_dir, '..'))  # Move one level up for the backup directory

    # Check if the 'plugins.backup' directory already exists
    backup_dir = os.path.join(backup_parent_dir, 'plugins.backup')
    if os.path.exists(backup_dir):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")  # Get current timestamp
        backup_dir += f"_{timestamp}"  # Append timestamp to the backup directory name

    try:
        # Copy the entire 'plugins' directory to the backup directory
        shutil.copytree(source_dir, backup_dir)
        log.info(f"Backup created successfully in {backup_dir}.")
    except shutil.Error as e:
        log.error(f"Error: {e}")
    except Exception as e:
        log.error(f"Error: {e}")

if __name__ == "__main__":
    backup_plugins()
