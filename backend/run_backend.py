#!/usr/bin/env python3
"""
Backend startup script that ensures correct working directory.
"""

import os
import sys

# Change to the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Add the current directory to Python path
sys.path.insert(0, script_dir)

# Now import and run the main application
if __name__ == "__main__":
    import uvicorn
    from main import app
    
    print(f"Starting backend from directory: {os.getcwd()}")
    print(f"Uploads directory exists: {os.path.exists('uploads')}")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
