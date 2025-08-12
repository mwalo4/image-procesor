#!/usr/bin/env python3
"""
Development server with auto-restart functionality
"""

import os
import sys
import time
import subprocess
import signal
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class RestartHandler(FileSystemEventHandler):
    def __init__(self, restart_callback):
        self.restart_callback = restart_callback
        self.last_restart = 0
        
    def on_modified(self, event):
        if event.is_directory:
            return
            
        # Ignore temporary files
        if event.src_path.endswith('.pyc') or '__pycache__' in event.src_path:
            return
            
        # Debounce restarts (max 1 restart per 2 seconds)
        current_time = time.time()
        if current_time - self.last_restart < 2:
            return
            
        print(f"🔄 Detected change in {event.src_path}")
        self.last_restart = current_time
        self.restart_callback()

class DevServer:
    def __init__(self):
        self.process = None
        self.observer = None
        self.running = True
        
    def start_server(self):
        """Start the Flask server"""
        if self.process:
            self.stop_server()
            
        print("🚀 Starting Flask server...")
        env = os.environ.copy()
        env['PORT'] = '8081'
        
        self.process = subprocess.Popen([
            sys.executable, 'api_server.py'
        ], env=env)
        
    def stop_server(self):
        """Stop the Flask server"""
        if self.process:
            print("🛑 Stopping Flask server...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None
            
    def restart_server(self):
        """Restart the Flask server"""
        print("🔄 Restarting server...")
        self.stop_server()
        time.sleep(1)  # Wait a bit before restarting
        self.start_server()
        
    def start_watcher(self):
        """Start file watching"""
        event_handler = RestartHandler(self.restart_server)
        self.observer = Observer()
        self.observer.schedule(event_handler, '.', recursive=True)
        self.observer.start()
        
    def stop_watcher(self):
        """Stop file watching"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            
    def run(self):
        """Run the development server"""
        print("🔧 Development server starting...")
        print("📁 Watching for file changes...")
        
        # Handle Ctrl+C gracefully
        def signal_handler(signum, frame):
            print("\n🛑 Shutting down development server...")
            self.running = False
            self.stop_server()
            self.stop_watcher()
            sys.exit(0)
            
        signal.signal(signal.SIGINT, signal_handler)
        
        try:
            self.start_server()
            self.start_watcher()
            
            print("✅ Development server running on http://localhost:8081")
            print("🔄 Server will automatically restart when files change")
            print("🛑 Press Ctrl+C to stop")
            
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    dev_server = DevServer()
    dev_server.run() 