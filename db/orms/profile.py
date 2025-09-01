import os
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, DateTime, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from db.orm_db_manager import DatabaseConnectionManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()

class Profile(Base):
    __tablename__ = "profiles"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role = Column(Enum('student', 'parent', 'teacher', name='role_type'), nullable=False)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Profile(user_id={self.user_id}, role='{self.role}', email='{self.email}')>"


class ProfileCRUD:
    db_manager = DatabaseConnectionManager(
        app_name="db/ORMs/profiles.py",
        database_name=os.environ.get("DB_NAME")
    )

    @classmethod
    def get_profile_by_user_id(cls, user_id: str):
        """Get profile by user ID"""
        try:
            with cls.db_manager.get_session() as session:
                return session.query(Profile).filter(Profile.user_id == user_id).first()
        except SQLAlchemyError as e:
            logger.error(f"ProfileCRUD get_profile_by_user_id error: {e}")
            raise

    @classmethod
    def get_profiles_by_role(cls, role: str):
        """Get all profiles by role"""
        try:
            with cls.db_manager.get_session() as session:
                return session.query(Profile).filter(Profile.role == role).all()
        except SQLAlchemyError as e:
            logger.error(f"ProfileCRUD get_profiles_by_role error: {e}")
            raise

    @classmethod
    def create_profile(cls, profile_data: dict):
        """Create a new profile"""
        try:
            with cls.db_manager.get_session() as session:
                profile = Profile(**profile_data)
                session.add(profile)
                session.commit()
                return profile
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"ProfileCRUD create_profile error: {e}")
            raise

    @classmethod
    def update_profile(cls, user_id: str, update_data: dict):
        """Update profile"""
        try:
            with cls.db_manager.get_session() as session:
                profile = session.query(Profile).filter(Profile.user_id == user_id).first()
                if not profile:
                    return None
                
                for key, value in update_data.items():
                    if hasattr(profile, key):
                        setattr(profile, key, value)
                
                session.commit()
                return profile
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"ProfileCRUD update_profile error: {e}")
            raise

    @classmethod
    def delete_profile(cls, user_id: str):
        """Delete profile"""
        try:
            with cls.db_manager.get_session() as session:
                profile = session.query(Profile).filter(Profile.user_id == user_id).first()
                if not profile:
                    return None
                
                session.delete(profile)
                session.commit()
                return user_id
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"ProfileCRUD delete_profile error: {e}")
            raise
