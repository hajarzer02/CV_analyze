#!/usr/bin/env python3
"""
Database migration script to add the 'role' column to the users table.
This script should be run before using the admin functionality.
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def migrate_add_role():
    """Add the 'role' column to the users table."""
    # Database URL from environment
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/cvdb")
    
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Check if the role column already exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'role'
            """))
            
            if result.fetchone():
                print("✅ Role column already exists in users table")
                return
            
            # Add the role column
            print("Adding 'role' column to users table...")
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN role VARCHAR DEFAULT 'user'
            """))
            
            # Update existing users to have 'user' role
            print("Setting default role for existing users...")
            conn.execute(text("""
                UPDATE users 
                SET role = 'user' 
                WHERE role IS NULL
            """))
            
            # Commit the changes
            conn.commit()
            
            print("✅ Migration completed successfully!")
            print("All existing users have been assigned the 'user' role")
            print("You can now create admin users using create_admin_user.py")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure your database is running")
        print("2. Check your DATABASE_URL in the .env file")
        print("3. Ensure you have the necessary permissions to alter the table")
        sys.exit(1)

if __name__ == "__main__":
    print("🔄 Database Migration: Adding 'role' column")
    print("=" * 50)
    migrate_add_role()


