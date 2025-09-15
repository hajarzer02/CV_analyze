#!/usr/bin/env python3
"""
Script to create an admin user for testing purposes.
Run this after setting up the database.
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_db, create_tables, User
from auth import get_password_hash
from sqlalchemy.orm import Session

def create_admin_user():
    """Create an admin user if it doesn't exist."""
    # Create tables first
    create_tables()
    
    # Get database session
    db = next(get_db())
    
    try:
        # Check if admin user already exists
        admin_user = db.query(User).filter(User.email == "admin@example.com").first()
        
        if admin_user:
            print("Admin user already exists!")
            return
        
        # Create admin user
        admin_user = User(
            name="Admin User",
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            is_active="true"
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"Admin user created successfully!")
        print(f"Email: admin@example.com")
        print(f"Password: admin123")
        
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
