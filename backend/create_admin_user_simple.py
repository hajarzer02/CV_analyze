#!/usr/bin/env python3
"""
Simple script to create an admin user without checking for role column existence.
Use this if the role column already exists but the main script is having issues.
"""

import os
import sys
from sqlalchemy.orm import Session
from database import get_db, create_tables, User
from auth import get_password_hash

def create_admin_user_simple():
    """Create an admin user without role column checks."""
    # Create tables first
    create_tables()
    
    # Get database session
    db = next(get_db())
    
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.role == 'admin').first()
        if existing_admin:
            print(f"Admin user already exists: {existing_admin.email}")
            return
        
        # Get admin details from user input
        print("Creating admin user...")
        name = input("Enter admin name: ").strip()
        email = input("Enter admin email: ").strip()
        password = input("Enter admin password: ").strip()
        
        if not name or not email or not password:
            print("Error: All fields are required")
            return
        
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"Error: User with email {email} already exists")
            return
        
        # Create admin user
        hashed_password = get_password_hash(password)
        admin_user = User(
            name=name,
            email=email,
            hashed_password=hashed_password,
            role='admin',
            is_active='true'
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"Admin user created successfully!")
        print(f"ID: {admin_user.id}")
        print(f"Name: {admin_user.name}")
        print(f"Email: {admin_user.email}")
        print(f"Role: {admin_user.role}")
        
    except Exception as e:
        print(f"Error creating admin user: {e}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error details: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user_simple()
