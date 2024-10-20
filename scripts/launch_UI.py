from fastapi import FastAPI
import uvicorn
import os
import sys
import webbrowser
from threading import Timer
import socket

# Add the project root to sys.path to ensure 'modules' can be imported
current_file_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(current_file_path))
sys.path.append(project_root)

def open_browser():
    """Function to open the web browser to the menu page."""
    webbrowser.open_new("http://localhost:8000/main_menu")

def is_port_in_use(host: str, port: int) -> bool:
    """Check if a port is already in use on the given host."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0

def start_server():
    """Function to start the FastAPI web server and open the browser."""
    if is_port_in_use('localhost', 8000):
        print("Server is already running. Opening browser...")
        open_browser()
    else:
        print("Starting new server...")
        # Launch the browser after a short delay to ensure the server is up
        Timer(1, open_browser).start()  # Wait 1 second before opening the browser
        # Pass the application as an import string to enable reload functionality
        uvicorn.run("modules.UI.routes:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    # Run the web server or open the browser if already running
    start_server()
