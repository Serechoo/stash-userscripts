import time                     ## If you encounter any errors while attempting to run this script that mention a missing module, simply run a pip install "Insert Missing Module Name Here" and try running again.
import os
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith('urls.txt'):
            source_path = event.src_path
            destination_path = r'C:\plugins\ytdlp\urls.txt' ## Where you want the file sent. This is typically C:\plugins\ytdlp\urls.txt (for Windows) to overwrite the existing file in that directory. Adjust if needed.
            
            # Add a delay before attempting to move the file
            time.sleep(2)  # Adjust this delay as needed
            
            try:
                shutil.move(source_path, destination_path)
                print(f"Moved 'urls.txt' from {source_path} to {destination_path}")
            except Exception as e:
                print(f"Error moving file: {e}")

def start_watching():
    event_handler = MyHandler()
    observer = Observer()
    directory_to_watch = r'C:\Path\To\Folder' ## Set this to the directory you want monitored eg. C:\Users\$User\Downloads

    observer.schedule(event_handler, directory_to_watch, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_watching()
