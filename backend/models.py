"""
Database Models for AI Co-founder SaaS
Multi-user architecture with SQLAlchemy
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, Float, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    """
    User table for multi-user support.
    Each user has their own account with authentication details.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # One-to-one relationship with Settings
    settings = relationship("Settings", back_populates="user", uselist=False, cascade="all, delete-orphan")

    # One-to-many relationship with ResearchReports
    reports = relationship("ResearchReport", back_populates="user", cascade="all, delete-orphan")


class Settings(Base):
    """
    Settings table for storing user-specific configuration.
    Replaces the old config.json file.
    """
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # Business Configuration
    industry = Column(String, default="AI SaaS")
    competitors = Column(JSON, default=list)  # List of competitor URLs
    report_language = Column(String, default="english")

    # Slack Integration
    slack_access_token = Column(String, nullable=True)
    slack_team_id = Column(String, nullable=True)
    slack_team_name = Column(String, nullable=True)
    slack_user_id = Column(String, nullable=True)
    slack_channel_id = Column(String, nullable=True)
    slack_installed = Column(Boolean, default=False)
    slack_installed_at = Column(DateTime, nullable=True)

    # Email Configuration (SendGrid)
    sendgrid_verified = Column(Boolean, default=False)

    # Monitoring Settings
    monitoring_enabled = Column(Boolean, default=True)
    daily_digest_enabled = Column(Boolean, default=True)
    weekly_report_enabled = Column(Boolean, default=True)
    competitor_alert_threshold = Column(Float, default=0.1)  # 10% change threshold

    # Metadata
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship back to User
    user = relationship("User", back_populates="settings")


class ResearchReport(Base):
    """
    Stores generated research reports for each user.
    """
    __tablename__ = "research_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    report_type = Column(String, nullable=False)  # 'weekly', 'competitor', 'monthly', 'validation'
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=True)
    content = Column(JSON, nullable=True)  # Store structured report data
    file_path = Column(String, nullable=True)  # Path to generated PDF/DOCX

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    is_sent = Column(Boolean, default=False)
    sent_via = Column(String, nullable=True)  # 'email', 'slack', 'both'

    # Relationship back to User
    user = relationship("User", back_populates="reports")


class CompetitorChange(Base):
    """
    Tracks detected changes in competitor websites.
    """
    __tablename__ = "competitor_changes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    competitor_url = Column(String, nullable=False)
    change_type = Column(String, nullable=False)  # 'price', 'feature', 'content'
    change_description = Column(Text, nullable=True)
    change_percentage = Column(Float, nullable=True)

    # Metadata
    detected_at = Column(DateTime, default=datetime.utcnow)
    is_notified = Column(Boolean, default=False)

    # Relationship back to User
    user = relationship("User")
