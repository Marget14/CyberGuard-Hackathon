# launcher.py
import multiprocessing
import subprocess
import time
import sys
import os

def start_api():
    # adjust path to your API file
    api_script = os.path.join(os.path.dirname(__file__), "CyberGuard_API.py")
    # Run as new python process, keep stdout/stderr for debugging
    subprocess.Popen([sys.executable, api_script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def start_gui():
    gui_script = os.path.join(os.path.dirname(__file__), "CyberGuard_Desktop_API.py")
    subprocess.Popen([sys.executable, gui_script])

if __name__ == "__main__":
    # start API first
    start_api()
    # wait a bit for API to become available
    time.sleep(1.5)
    # then start GUI
    start_gui()
