#!/usr/bin/env python3
"""
Simple HTTP Server for CRV Dashboard
Serves the web interface for the CRV prediction system
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path

class CRVHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.getcwd(), **kwargs)

    def end_headers(self):
        # Add CORS headers to allow browser access
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

def main():
    # Check if required files exist
    required_files = ['index.html', 'styles.css', 'script.js', 'crv_predictions.csv']
    missing_files = [f for f in required_files if not Path(f).exists()]

    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        print("Please ensure all files are present before starting the server.")
        sys.exit(1)

    # Server configuration
    PORT = 8000
    try:
        with socketserver.TCPServer(("", PORT), CRVHandler) as httpd:
            print("🚀 CRV Dashboard Server Starting...")
            print(f"📊 Server running at: http://localhost:{PORT}")
            print(f"📁 Serving directory: {os.getcwd()}")
            print("🔄 Press Ctrl+C to stop the server")
            # Automatically open browser
            try:
                webbrowser.open(f'http://localhost:{PORT}')
                print("🌐 Browser opened automatically")
            except:
                print("💡 Manually open http://localhost:8000 in your browser")
            print("\n" + "="*50)
            httpd.serve_forever()

    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {PORT} is already in use. Try a different port or stop the existing server.")
        else:
            print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
