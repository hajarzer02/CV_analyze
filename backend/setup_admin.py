#!/usr/bin/env python3
"""
Setup script to migrate the database and create an admin user.
This script handles the complete setup process for admin functionality.
"""

import os
import sys
import subprocess

def run_migration():
    """Run the database migration."""
    print("🔄 Running database migration...")
    try:
        result = subprocess.run([sys.executable, "migrate_database.py"], 
                              capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            print("✅ Migration completed successfully")
            return True
        else:
            print(f"❌ Migration failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error running migration: {e}")
        return False

def create_admin():
    """Create admin user."""
    print("\n👤 Creating admin user...")
    try:
        result = subprocess.run([sys.executable, "create_admin_user.py"], 
                              cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            print("✅ Admin user creation completed")
            return True
        else:
            print("❌ Admin user creation failed")
            return False
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Setting up Admin Functionality")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("database.py"):
        print("❌ Please run this script from the backend directory")
        sys.exit(1)
    
    # Run migration
    if not run_migration():
        print("\n❌ Setup failed at migration step")
        sys.exit(1)
    
    # Create admin user
    if not create_admin():
        print("\n❌ Setup failed at admin user creation step")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✅ Admin functionality setup completed successfully!")
    print("\nNext steps:")
    print("1. Start the backend server: python main.py")
    print("2. Start the frontend: npm start (in frontend directory)")
    print("3. Login with your admin credentials")
    print("4. Navigate to /admin to access the admin panel")

if __name__ == "__main__":
    main()


