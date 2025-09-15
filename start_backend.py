#!/usr/bin/env python3
"""
Root-level backend startup script.
This ensures the backend runs from the correct directory.
"""

import os
import sys
import subprocess

def main():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(script_dir, 'backend')
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    print(f"Starting backend from directory: {os.getcwd()}")
    print(f"Uploads directory exists: {os.path.exists('uploads')}")
    
    # Run the backend
    try:
        import uvicorn
        from main import app
        
        print("Starting FastAPI backend on http://localhost:8000")
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except ImportError:
        print("FastAPI not available, trying Flask app...")
        try:
            from app import app
            print("Starting Flask backend on http://localhost:5000")
            app.run(debug=True, host='0.0.0.0', port=5000)
        except ImportError as e:
            print(f"Error: {e}")
            print("Please install the required dependencies:")
            print("cd backend && pip install -r requirements.txt")

if __name__ == "__main__":
    main()
