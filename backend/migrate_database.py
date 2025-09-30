#!/usr/bin/env python3
"""
Comprehensive database migration script.
This script handles adding the 'role' column to the users table for different database types.
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

load_dotenv()

def get_database_type(database_url):
    """Determine the database type from the URL."""
    if database_url.startswith('postgresql'):
        return 'postgresql'
    elif database_url.startswith('sqlite'):
        return 'sqlite'
    elif database_url.startswith('mysql'):
        return 'mysql'
    else:
        return 'unknown'

def check_column_exists(conn, table_name, column_name, db_type):
    """Check if a column exists in a table."""
    if db_type == 'postgresql':
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = :table_name AND column_name = :column_name
        """), {"table_name": table_name, "column_name": column_name})
    elif db_type == 'sqlite':
        result = conn.execute(text("PRAGMA table_info(users)"))
        columns = [row[1] for row in result.fetchall()]
        return column_name in columns
    elif db_type == 'mysql':
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = :table_name AND column_name = :column_name
        """), {"table_name": table_name, "column_name": column_name})
    else:
        return False
    
    return result.fetchone() is not None

def migrate_add_role():
    """Add the 'role' column to the users table."""
    # Database URL from environment
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/cvdb")
    db_type = get_database_type(DATABASE_URL)
    
    print(f"Database type: {db_type}")
    print(f"Database URL: {DATABASE_URL}")
    
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Check if users table exists
            inspector = inspect(engine)
            if 'users' not in inspector.get_table_names():
                print("❌ Users table does not exist. Please run the main application first to create tables.")
                return
            
            # Check if the role column already exists
            if check_column_exists(conn, 'users', 'role', db_type):
                print("✅ Role column already exists in users table")
                return
            
            # Add the role column based on database type
            print("Adding 'role' column to users table...")
            
            if db_type == 'postgresql':
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN role VARCHAR DEFAULT 'user'
                """))
            elif db_type == 'sqlite':
                # SQLite doesn't support ALTER TABLE ADD COLUMN with DEFAULT easily
                # We'll add the column and then update it
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN role VARCHAR
                """))
            elif db_type == 'mysql':
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN role VARCHAR(50) DEFAULT 'user'
                """))
            else:
                print(f"❌ Unsupported database type: {db_type}")
                return
            
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
        print("4. For SQLite, make sure the database file exists and is writable")
        sys.exit(1)

def main():
    """Main migration function."""
    print("🔄 Database Migration: Adding 'role' column")
    print("=" * 50)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  No .env file found. Using default database URL.")
        print("   Consider creating a .env file with your database configuration.")
    
    migrate_add_role()

if __name__ == "__main__":
    main()






