"""
Script to share the NFL analysis website with friends on different networks.
Uses ngrok to create a public URL.
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path
import config

def check_ngrok():
    """Check if ngrok is installed."""
    try:
        result = subprocess.run(['ngrok', 'version'], 
                              capture_output=True, text=True, timeout=5)
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

def install_ngrok_instructions():
    """Print instructions for installing ngrok."""
    print("\n" + "="*60)
    print("NGROK NOT FOUND")
    print("="*60)
    print("\nTo share with friends on different networks, you need ngrok.")
    print("\nInstallation:")
    print("1. Visit: https://ngrok.com/download")
    print("2. Download for macOS")
    print("3. Unzip and move ngrok to /usr/local/bin/ (or add to PATH)")
    print("   Or run: sudo mv ngrok /usr/local/bin/")
    print("\nAlternative: Use Homebrew:")
    print("   brew install ngrok/ngrok/ngrok")
    print("\nAfter installing, run this script again.")
    print("="*60)

def start_server():
    """Start the local web server."""
    print("\n[1/3] Starting local web server...")
    
    # Generate website if it doesn't exist
    website_file = Path(config.OUTPUT_DIR) / "mobile_website.html"
    if not website_file.exists():
        print("   Generating website...")
        import generate_website
        generate_website.generate_mobile_website()
    
    # Start server in background
    import http.server
    import socketserver
    import os
    import threading
    
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
    
    # Wait for server to start
    time.sleep(2)
    print(f"   ✓ Server running on http://localhost:{PORT}")
    return httpd

def start_ngrok_tunnel(port=8000):
    """Start ngrok tunnel."""
    print("\n[2/3] Starting ngrok tunnel...")
    
    try:
        # Start ngrok
        ngrok_process = subprocess.Popen(
            ['ngrok', 'http', str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment for ngrok to start
        time.sleep(3)
        
        # Get the public URL from ngrok API
        import requests
        try:
            response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
            if response.status_code == 200:
                data = response.json()
                tunnels = data.get('tunnels', [])
                if tunnels:
                    public_url = tunnels[0].get('public_url')
                    print(f"   ✓ Public URL: {public_url}")
                    print(f"   ✓ Share this with your friends: {public_url}/mobile_website.html")
                    return public_url, ngrok_process
        except:
            pass
        
        print("   ✓ Ngrok tunnel started (check ngrok web interface at http://127.0.0.1:4040)")
        print("   ✓ Look for the 'Forwarding' URL and share it with friends")
        return None, ngrok_process
        
    except Exception as e:
        print(f"   ✗ Error starting ngrok: {e}")
        return None, None

def main():
    """Main function to share website with friends."""
    print("="*60)
    print("SHARE NFL ANALYSIS WITH FRIENDS")
    print("="*60)
    
    # Check if ngrok is installed
    if not check_ngrok():
        install_ngrok_instructions()
        return
    
    # Start local server
    httpd = start_server()
    
    # Start ngrok tunnel
    public_url, ngrok_process = start_ngrok_tunnel(8000)
    
    if public_url:
        share_url = f"{public_url}/mobile_website.html"
        print("\n" + "="*60)
        print("READY TO SHARE!")
        print("="*60)
        print(f"\nShare this URL with your friends:")
        print(f"  {share_url}")
        print(f"\nThey can open it on their phones, tablets, or computers!")
        print(f"\nThe tunnel will stay active until you press Ctrl+C")
        print("="*60)
        
        # Try to open in browser
        try:
            webbrowser.open(f"http://127.0.0.1:4040")  # Ngrok web interface
        except:
            pass
    else:
        print("\n" + "="*60)
        print("NGROK STARTED")
        print("="*60)
        print("\n1. Open ngrok web interface: http://127.0.0.1:4040")
        print("2. Look for the 'Forwarding' URL (starts with https://)")
        print("3. Share that URL + '/mobile_website.html' with friends")
        print("\nExample: https://abc123.ngrok.io/mobile_website.html")
        print("="*60)
    
    try:
        print("\nPress Ctrl+C to stop sharing...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping...")
        if ngrok_process:
            ngrok_process.terminate()
        httpd.shutdown()
        print("✓ Server stopped. Your friends can no longer access it.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nStopped by user.")

