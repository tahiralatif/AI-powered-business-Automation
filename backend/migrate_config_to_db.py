"""
Migration Script: config.json to Database
Imports existing config.json data into the new multi-user database structure.

Usage:
    python migrate_config_to_db.py
"""
import json
import os
import sys
from datetime import datetime

# Fix Windows console encoding for emoji support
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import bcrypt

from database import init_db, get_db_session
from models import User, Settings


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def migrate_config_to_db():
    """
    Migrate data from config.json to the database.
    Creates a default user with the existing configuration.
    """
    # Initialize database
    init_db()
    
    # Load config.json
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    
    if not os.path.exists(config_path):
        print("⚠️ config.json not found. Skipping migration.")
        return
    
    with open(config_path, "r") as f:
        config = json.load(f)
    
    print(f"📄 Loaded config.json: {config}")
    
    db = get_db_session()
    
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            User.email == config.get("email_address", "founder@example.com")
        ).first()
        
        if existing_user:
            print(f"⚠️ User {existing_user.email} already exists in database.")
            print("ℹ️ Updating existing user's settings...")
            user = existing_user
        else:
            # Create user from config
            email = config.get("email_address", "founder@example.com")
            user = User(
                email=email,
                hashed_password=hash_password("changeme123"),  # Default password
                full_name="Founding User",
                is_active=True,
                is_verified=False
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"✅ Created user: {user.email}")
        
        # Check if settings already exist
        existing_settings = db.query(Settings).filter(Settings.user_id == user.id).first()
        
        if existing_settings:
            print("ℹ️ Updating existing settings...")
            settings = existing_settings
        else:
            settings = Settings(user_id=user.id)
            db.add(settings)
        
        # Map config.json fields to Settings
        settings.industry = config.get("industry", settings.industry)
        settings.competitors = config.get("competitors", [])
        settings.report_language = config.get("report_language", "english")
        settings.monitoring_enabled = config.get("monitoring_enabled", True)
        
        # Map Slack webhook to OAuth (if available)
        slack_webhook = config.get("slack_webhook_url", "")
        if slack_webhook:
            print("ℹ️ Note: Slack webhook found. Consider migrating to Slack OAuth for better integration.")
        
        settings.last_updated = datetime.utcnow()
        
        db.commit()
        
        print("\n" + "="*50)
        print("✅ MIGRATION COMPLETE!")
        print("="*50)
        print(f"User Email: {user.email}")
        print(f"Industry: {settings.industry}")
        print(f"Competitors: {len(settings.competitors)} URLs")
        print(f"Monitoring Enabled: {settings.monitoring_enabled}")
        print("\n⚠️  IMPORTANT:")
        print("  - Default password: changeme123")
        print("  - Please change password after first login")
        print("  - Configure SendGrid API key in .env for email delivery")
        print("  - Configure Slack OAuth in .env for 'Add to Slack' button")
        print("="*50 + "\n")
        
        return {
            "success": True,
            "user_id": user.id,
            "email": user.email,
            "settings_id": settings.id
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ Migration failed: {e}")
        return {"success": False, "error": str(e)}
    finally:
        db.close()


def create_sample_data():
    """
    Create sample data for testing the multi-user system.
    """
    db = get_db_session()
    
    try:
        # Sample User 1
        user1 = User(
            email="tahira@example.com",
            hashed_password=hash_password("password123"),
            full_name="Tahira Founder",
            is_active=True,
            is_verified=True
        )
        db.add(user1)
        db.commit()
        
        settings1 = Settings(
            user_id=user1.id,
            industry="AI SaaS",
            competitors=["https://www.tome.app", "https://gamma.app"],
            report_language="english",
            monitoring_enabled=True,
            slack_installed=False
        )
        db.add(settings1)
        
        # Sample User 2
        user2 = User(
            email="ahmed@example.com",
            hashed_password=hash_password("password123"),
            full_name="Ahmed Entrepreneur",
            is_active=True,
            is_verified=False
        )
        db.add(user2)
        db.commit()
        
        settings2 = Settings(
            user_id=user2.id,
            industry="E-commerce",
            competitors=["https://www.shopify.com", "https://www.wix.com"],
            report_language="urdu",
            monitoring_enabled=True,
            slack_installed=False
        )
        db.add(settings2)
        
        db.commit()
        
        print("✅ Sample data created successfully!")
        print(f"  User 1: tahira@example.com / password123")
        print(f"  User 2: ahmed@example.com / password123")
        
        return {"success": True}
        
    except Exception as e:
        db.rollback()
        print(f"❌ Sample data creation failed: {e}")
        return {"success": False, "error": str(e)}
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Starting config.json to Database Migration...\n")
    migrate_config_to_db()
    
    # Uncomment to create sample test data
    # print("\n📝 Creating sample test data...")
    # create_sample_data()
