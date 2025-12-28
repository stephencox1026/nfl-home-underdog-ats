"""
Simple HTTP server to serve the mobile website locally.
"""

import http.server
import socketserver
import os
from pathlib import Path
import config

PORT = 8000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

def main():
    # Change to outputs directory
    os.chdir(config.OUTPUT_DIR)
    
    handler = MyHTTPRequestHandler
    
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"Server started at http://localhost:{PORT}")
        print(f"Serving files from: {Path(config.OUTPUT_DIR).absolute()}")
        print(f"\nOpen in browser: http://localhost:{PORT}/mobile_website.html")
        print(f"\nTo share with friends on your network:")
        print(f"  - Find your local IP: ifconfig (Mac/Linux) or ipconfig (Windows)")
        print(f"  - Share: http://YOUR_IP:{PORT}/mobile_website.html")
        print(f"\nPress Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    main()

