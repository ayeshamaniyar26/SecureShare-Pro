"""
HTTP Server implementation with bandwidth monitoring
"""

import os
import socketserver
import http.server
from pathlib import Path
from datetime import datetime
import threading
import time


class BandwidthTracker:
    """Track bandwidth usage for uploads and downloads"""

    def __init__(self):
        self.download_bytes = 0
        self.upload_bytes = 0
        self.start_time = time.time()
        self.lock = threading.Lock()

    def add_download(self, bytes_num):
        with self.lock:
            self.download_bytes += bytes_num

    def add_upload(self, bytes_num):
        with self.lock:
            self.upload_bytes += bytes_num

    def get_stats(self):
        with self.lock:
            elapsed = time.time() - self.start_time
            download_speed = self.download_bytes / elapsed if elapsed > 0 else 0
            upload_speed = self.upload_bytes / elapsed if elapsed > 0 else 0
            return {
                'download_bytes': self.download_bytes,
                'upload_bytes': self.upload_bytes,
                'download_speed': download_speed,
                'upload_speed': upload_speed,
                'elapsed': elapsed
            }

    def reset(self):
        with self.lock:
            self.download_bytes = 0
            self.upload_bytes = 0
            self.start_time = time.time()


class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP handler with bandwidth tracking and logging"""

    bandwidth_tracker = BandwidthTracker()
    share_path = None
    password = None
    activity_callback = None

    def do_GET(self):
        """Handle GET requests with bandwidth tracking"""
        # Password protection
        if self.password:
            auth = self.headers.get('Authorization')
            if not auth or not self.check_auth(auth):
                self.send_auth_required()
                return

        # Track activity
        if self.activity_callback:
            self.activity_callback('GET', self.path)

        # Serve file and track bandwidth
        try:
            # Call parent's do_GET
            f = self.send_head()
            if f:
                try:
                    self.copyfile(f, self.wfile)
                finally:
                    f.close()
        except Exception as e:
            print(f"Error in GET: {e}")

    def check_auth(self, auth_header):
        """Check password authorization"""
        import base64
        try:
            auth_type, auth_string = auth_header.split(' ', 1)
            if auth_type.lower() == 'basic':
                decoded = base64.b64decode(auth_string).decode('utf-8')
                username, password = decoded.split(':', 1)
                return password == self.password
        except Exception:
            pass
        return False

    def send_auth_required(self):
        """Send 401 authentication required"""
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm="SecureShare"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'Authentication required')

    def log_message(self, format, *args):
        """Custom logging"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {format % args}")


class FileServer:
    """Manages the HTTP file server"""

    def __init__(self, share_path, port, password=None, activity_callback=None):
        self.share_path = Path(share_path)
        self.port = port
        self.password = password
        self.activity_callback = activity_callback
        self.server = None
        self.server_thread = None
        self.running = False
        self.original_dir = os.getcwd()

        # Set class variables for handler
        CustomHTTPRequestHandler.share_path = str(self.share_path)
        CustomHTTPRequestHandler.password = password
        CustomHTTPRequestHandler.activity_callback = activity_callback

    def start(self):
        """Start the HTTP server"""
        try:
            # Change to the directory to serve
            if self.share_path.is_file():
                # If it's a file, serve its parent directory
                os.chdir(self.share_path.parent)
            else:
                # If it's a directory, serve it
                os.chdir(self.share_path)

            self.server = socketserver.TCPServer(
                ("", self.port),
                CustomHTTPRequestHandler
            )
            self.server.allow_reuse_address = True

            self.running = True
            self.server_thread = threading.Thread(
                target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()

            print(f"Server started on port {self.port}")
            print(f"Serving: {self.share_path}")
            return True
        except Exception as e:
            print(f"Error starting server: {e}")
            os.chdir(self.original_dir)
            return False

    def stop(self):
        """Stop the HTTP server"""
        if self.server:
            self.running = False
            self.server.shutdown()
            self.server.server_close()
            os.chdir(self.original_dir)
            print("Server stopped")

    def get_bandwidth_stats(self):
        """Get current bandwidth statistics"""
        return CustomHTTPRequestHandler.bandwidth_tracker.get_stats()

    def reset_bandwidth_stats(self):
        """Reset bandwidth statistics"""
        CustomHTTPRequestHandler.bandwidth_tracker.reset()
