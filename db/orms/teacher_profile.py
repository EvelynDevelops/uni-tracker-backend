import os
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from db.orm_db_manager import DatabaseConnectionManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()

class TeacherProfile(Base):
    __tablename__ = "teacher_profile"

    user_id = Column(UUID(as_uuid=True), ForeignKey('profiles.user_id'), primary_key=True)
    subjects = Column(ARRAY(String), nullable=True)
    organization = Column(Text, nullable=True)
    timezone = Column(Text, nullable=True)
    bio = Column(Text, nullable=True)
    max_advisees = Column(Integer, default=50)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    profile = relationship("Profile", backref="teacher_profile")

    def __repr__(self):
        return f"<TeacherProfile(user_id={self.user_id}, organization='{self.organization}')>"


class TeacherProfileCRUD:
    db_manager = DatabaseConnectionManager(
        app_name="db/ORMs/teacher_profile.py",
        database_name=os.environ.get("DB_NAME")
    )

    @classmethod
    def get_teacher_profile_by_user_id(cls, user_id: str):
        """Get teacher profile by user ID"""
        try:
            with cls.db_manager.get_session() as session:
                return session.query(TeacherProfile).filter(TeacherProfile.user_id == user_id).first()
        except SQLAlchemyError as e:
            logger.error(f"TeacherProfileCRUD get_teacher_profile_by_user_id error: {e}")
            raise

    @classmethod
    def get_teachers_by_subject(cls, subject: str):
        """Get teachers by subject"""
        try:
            with cls.db_manager.get_session() as session:
                return session.query(TeacherProfile).filter(TeacherProfile.subjects.contains([subject])).all()
        except SQLAlchemyError as e:
            logger.error(f"TeacherProfileCRUD get_teachers_by_subject error: {e}")
            raise

    @classmethod
    def create_teacher_profile(cls, profile_data: dict):
        """Create a new teacher profile"""
        try:
            with cls.db_manager.get_session() as session:
                profile = TeacherProfile(**profile_data)
                session.add(profile)
                session.commit()
                return profile
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"TeacherProfileCRUD create_teacher_profile error: {e}")
            raise

    @classmethod
    def update_teacher_profile(cls, user_id: str, update_data: dict):
        """Update teacher profile"""
        try:
            with cls.db_manager.get_session() as session:
                profile = session.query(TeacherProfile).filter(TeacherProfile.user_id == user_id).first()
                if not profile:
                    return None
                
                for key, value in update_data.items():
                    if hasattr(profile, key):
                        setattr(profile, key, value)
                
                session.commit()
                return profile
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"TeacherProfileCRUD update_teacher_profile error: {e}")
            raise

    @classmethod
    def delete_teacher_profile(cls, user_id: str):
        """Delete teacher profile"""
        try:
            with cls.db_manager.get_session() as session:
                profile = session.query(TeacherProfile).filter(TeacherProfile.user_id == user_id).first()
                if not profile:
                    return None
                
                session.delete(profile)
                session.commit()
                return user_id
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"TeacherProfileCRUD delete_teacher_profile error: {e}")
            raise
