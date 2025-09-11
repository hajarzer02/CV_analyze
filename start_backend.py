#!/usr/bin/env python3
"""
Startup script for the CV Analysis backend.
This script will:
1. Check if PostgreSQL is running
2. Create the database if it doesn't exist
3. Start the FastAPI server
"""

import os
import sys
import subprocess
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

def check_postgresql():
    """Check if PostgreSQL is running and accessible."""
    try:
        # Try to connect to PostgreSQL
        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="postgres",
            database="postgres"
        )
        conn.close()
        print("✓ PostgreSQL is running")
        return True
    except Exception as e:
        print(f"✗ PostgreSQL connection failed: {e}")
        print("Please ensure PostgreSQL is running and accessible")
        return False

def create_database():
    """Create the CV database if it doesn't exist."""
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="postgres",
            database="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'cvdb'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute("CREATE DATABASE cvdb")
            print("✓ Database 'cvdb' created")
        else:
            print("✓ Database 'cvdb' already exists")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Database creation failed: {e}")
        return False

def start_server():
    """Start the FastAPI server."""
    try:
        print("🚀 Starting FastAPI server...")
        print("📖 API Documentation: http://localhost:8000/docs")
        print("🌐 API Base URL: http://localhost:8000")
        print("Press Ctrl+C to stop the server")
        print("-" * 50)
        
        # Start the server
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"✗ Server startup failed: {e}")

def main():
    """Main startup function."""
    print("🔧 CV Analysis Backend Startup")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Check PostgreSQL
    if not check_postgresql():
        print("\n💡 To install PostgreSQL:")
        print("   - Windows: Download from https://www.postgresql.org/download/windows/")
        print("   - macOS: brew install postgresql")
        print("   - Ubuntu: sudo apt-get install postgresql postgresql-contrib")
        return
    
    # Create database
    if not create_database():
        return
    
    # Start server
    start_server()

if __name__ == "__main__":
    main()
