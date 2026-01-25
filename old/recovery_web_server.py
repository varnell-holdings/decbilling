"""
Simple Web Server for Doctor Preferences App
This starts a local web server so the app can load files properly.
Usage:
    python start_server.py
Then open your browser to: http://localhost:8000
"""
import http.server
import socketserver
import webbrowser
import os
import json

PORT = 8000

# Change to the directory where this script is located
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def get_last_modified():
    """Get the last modified time of your data file"""
    # Replace 'your_data_file.txt' with whatever file changes when jobs are logged
    return os.path.getmtime("your_data_file.txt")


class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Handle the check_updates endpoint
        if self.path == "/check_updates":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            response = {"last_modified": get_last_modified()}
            self.wfile.write(json.dumps(response).encode())
        else:
            # Handle normal file requests
            super().do_GET()


print("=" * 60)
print("Doctor Preferences Web Server")
print("=" * 60)
print(f"\nStarting server on port {PORT}...")
print(f"\nOpen your browser to: http://localhost:{PORT}")
print(f"Or click this link: http://localhost:{PORT}/doctor_preferences.html")
print("\nPress Ctrl+C to stop the server")
print("=" * 60)

# Automatically open browser
try:
    webbrowser.open(f"http://localhost:{PORT}/doctor_preferences.html")
    print("\n✓ Browser opened automatically")
except:
    print("\n! Could not open browser automatically - please open manually")

# Start the server with custom handler
with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
