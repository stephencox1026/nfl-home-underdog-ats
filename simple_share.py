"""
Simple sharing solution - shows instructions for ngrok setup
"""

import subprocess
import sys
import time
import http.server
import socketserver
import threading
import os
from pathlib import Path
import config

def start_server():
    """Start the local web server."""
    os.chdir(config.OUTPUT_DIR)
    PORT = 8000
    
    class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
            self.send_header('Access-Control-Allow-Origin', '*')
            super().end_headers()
    
    handler = MyHTTPRequestHandler
    httpd = socketserver.TCPServer(("", PORT), handler)
    httpd.allow_reuse_address = True
    
    def run_server():
        httpd.serve_forever()
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(1)
    return httpd

def main():
    print("="*60)
    print("NFL ANALYSIS - SHARE WITH FRIENDS")
    print("="*60)
    
    # Generate website if needed
    website_file = Path(config.OUTPUT_DIR) / "mobile_website.html"
    if not website_file.exists():
        print("\n[1/3] Generating website...")
        import generate_website
        generate_website.generate_mobile_website()
        print("   ✓ Website generated")
    else:
        print("\n[1/3] Website already exists")
    
    # Start server
    print("\n[2/3] Starting local server...")
    httpd = start_server()
    print(f"   ✓ Server running on http://localhost:8000")
    
    # Check ngrok
    print("\n[3/3] Setting up ngrok...")
    ngrok_path = Path(__file__).parent / "ngrok"
    
    if not ngrok_path.exists():
        print("   ✗ Ngrok not found in project directory")
        print("\n   Please download ngrok from: https://ngrok.com/download")
        print("   Or run: curl -o ngrok.zip https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-darwin-amd64.zip")
        return
    
    # Check if ngrok needs auth
    print("   Checking ngrok setup...")
    
    try:
        # Try to start ngrok and capture output
        process = subprocess.Popen(
            [str(ngrok_path), "http", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        time.sleep(3)
        
        # Check if ngrok API is accessible
        import requests
        try:
            response = requests.get('http://localhost:4040/api/tunnels', timeout=2)
            if response.status_code == 200:
                data = response.json()
                tunnels = data.get('tunnels', [])
                if tunnels:
                    public_url = tunnels[0].get('public_url')
                    share_url = f"{public_url}/mobile_website.html"
                    print(f"\n" + "="*60)
                    print("✅ READY TO SHARE!")
                    print("="*60)
                    print(f"\nShare this URL with your friends:")
                    print(f"  {share_url}")
                    print(f"\nThey can open it on any device!")
                    print("="*60)
                    print("\nPress Ctrl+C to stop sharing...")
                    try:
                        while True:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        print("\n\nStopping...")
                        process.terminate()
                        httpd.shutdown()
                        print("✓ Stopped")
                    return
        except:
            pass
        
        # If we get here, ngrok might need auth
        print("\n" + "="*60)
        print("NGROK SETUP REQUIRED")
        print("="*60)
        print("\nNgrok needs to be authenticated. Here's how:")
        print("\n1. Sign up for free at: https://dashboard.ngrok.com/signup")
        print("2. Get your authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken")
        print("3. Run this command:")
        print(f"   ./ngrok config add-authtoken YOUR_TOKEN_HERE")
        print("\nThen run this script again!")
        print("="*60)
        
        # Keep server running
        print("\nLocal server is running on http://localhost:8000")
        print("Press Ctrl+C to stop...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nStopping...")
            process.terminate()
            httpd.shutdown()
            print("✓ Stopped")
            
    except Exception as e:
        print(f"\n   ✗ Error: {e}")
        print("\nAlternative: Use the ngrok web interface")
        print("1. In another terminal, run: ./ngrok http 8000")
        print("2. Visit: http://127.0.0.1:4040")
        print("3. Copy the Forwarding URL and add '/mobile_website.html'")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nStopped by user.")

