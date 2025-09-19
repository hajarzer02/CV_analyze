#!/usr/bin/env python3
"""
Script to create an admin user for the CV Analysis application.
Run this script to create the first admin user.
"""

import os
import sys
from sqlalchemy.orm import Session
from database import get_db, create_tables, User
from auth import get_password_hash

def create_admin_user():
    """Create an admin user."""
    # Create tables first
    create_tables()
    
    # Get database session
    db = next(get_db())
    
    try:
        # Check if role column exists, if not, run migration
        try:
            # Try to query the role column using SQLAlchemy text
            from sqlalchemy import text
            result = db.execute(text("SELECT role FROM users LIMIT 1"))
            result.fetchone()  # Actually execute the query
        except Exception as e:
            if "role" in str(e).lower() or "column" in str(e).lower():
                print("❌ Role column doesn't exist in the database.")
                print("Please run the migration script first:")
                print("   python migrate_database.py")
                return
            else:
                raise e
        
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
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()