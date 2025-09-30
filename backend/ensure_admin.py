#!/usr/bin/env python3
"""
Non-interactive script to insert or update an admin user directly in the database.

- Uses DATABASE_URL from environment (falls back to SQLite in backend folder if unset)
- Username/email from ADMIN_USERNAME (default: 'admin')
- Password from ADMIN_PASSWORD (default: 'ChangeMeNow123!')
- Name from ADMIN_NAME (default: 'Administrator')

Run:
  python backend/ensure_admin.py
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{os.path.join(os.path.dirname(__file__), 'app.db')}"
)

# Lazy import to reuse existing hashing policy (bcrypt via passlib)
from auth import get_password_hash

def main() -> None:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
        admin_name = os.getenv("ADMIN_NAME", "Administrator")
        admin_password = os.getenv("ADMIN_PASSWORD", "ChangeMeNow123!")
        # Handle bcrypt 72-byte limit defensively
        try:
            hashed = get_password_hash(admin_password)
        except Exception as e:
            msg = str(e)
            if '72 bytes' in msg or '72' in msg:
                print('⚠️  Admin password exceeds bcrypt 72-byte limit; truncating to 72 bytes before hashing.')
                safe_pw = admin_password[:72]
                hashed = get_password_hash(safe_pw)
            else:
                raise

        # Ensure users table exists minimally (works with existing schema)
        # Rely on existing migrations/startup to create tables; here we fail fast if not present
        try:
            session.execute(text("SELECT 1 FROM users LIMIT 1"))
        except Exception as e:
            raise RuntimeError("users table is missing; run the app or migration to create tables") from e

        # If a user exists with this email, update to admin and reset password
        existing = session.execute(
            text("SELECT id, role FROM users WHERE email = :email"),
            {"email": admin_email}
        ).mappings().first()

        if existing:
            session.execute(
                text(
                    """
                    UPDATE users
                    SET role = 'admin', hashed_password = :hpw, is_active = 'true'
                    WHERE email = :email
                    """
                ),
                {"hpw": hashed, "email": admin_email}
            )
            session.commit()
            print(f"✅ Updated existing user '{admin_email}' to admin and set a new password.")
            return

        # Otherwise insert a new admin row
        session.execute(
            text(
                """
                INSERT INTO users (name, email, hashed_password, is_active, role, created_at, updated_at)
                VALUES (:name, :email, :hpw, 'true', 'admin', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """
            ),
            {"name": admin_name, "email": admin_email, "hpw": hashed}
        )
        session.commit()
        print(f"✅ Inserted admin user '{admin_email}'.")
    finally:
        session.close()

if __name__ == "__main__":
    main()


