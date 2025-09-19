#!/usr/bin/env python3
"""
Debug script to check database schema and role column status.
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

load_dotenv()

def debug_database():
    """Debug the database schema."""
    # Database URL from environment
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:passroot@localhost:5432/cvdb")
    
    print("🔍 Database Debug Information")
    print("=" * 50)
    print(f"Database URL: {DATABASE_URL}")
    
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Check if users table exists
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            print(f"Tables in database: {tables}")
            
            if 'users' not in tables:
                print("❌ Users table does not exist!")
                return
            
            # Get column information
            columns = inspector.get_columns('users')
            print(f"\nColumns in users table:")
            for col in columns:
                print(f"  - {col['name']}: {col['type']} (nullable: {col['nullable']}, default: {col.get('default', 'None')})")
            
            # Check if role column exists
            column_names = [col['name'] for col in columns]
            if 'role' in column_names:
                print("\n✅ Role column exists!")
                
                # Try to query the role column
                try:
                    result = conn.execute(text("SELECT id, name, email, role FROM users LIMIT 5"))
                    rows = result.fetchall()
                    print(f"\nSample users data:")
                    for row in rows:
                        print(f"  ID: {row[0]}, Name: {row[1]}, Email: {row[2]}, Role: {row[3]}")
                except Exception as e:
                    print(f"❌ Error querying role column: {e}")
            else:
                print("\n❌ Role column does not exist!")
                
                # Try to add it
                print("\nAttempting to add role column...")
                try:
                    conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR DEFAULT 'user'"))
                    conn.execute(text("UPDATE users SET role = 'user' WHERE role IS NULL"))
                    conn.commit()
                    print("✅ Role column added successfully!")
                except Exception as e:
                    print(f"❌ Error adding role column: {e}")
            
    except Exception as e:
        print(f"❌ Database connection error: {e}")

if __name__ == "__main__":
    debug_database()
