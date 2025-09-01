import os
import uuid
from typing import List, Optional
from sqlalchemy import Column, String, Integer, Numeric, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from db.orm_db_manager import DatabaseConnectionManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()

class StudentProfile(Base):
    __tablename__ = "student_profile"

    user_id = Column(UUID(as_uuid=True), ForeignKey('profiles.user_id'), primary_key=True)
    graduation_year = Column(Integer, nullable=True)
    gpa = Column(Numeric(3, 2), nullable=True)
    sat_score = Column(Integer, nullable=True)
    act_score = Column(Integer, nullable=True)
    target_countries = Column(ARRAY(String), nullable=True)
    intended_majors = Column(ARRAY(String), nullable=True)

    # Relationship
    profile = relationship("Profile", backref="student_profile")

    def __repr__(self):
        return f"<StudentProfile(user_id={self.user_id}, graduation_year={self.graduation_year})>"


class StudentProfileCRUD:
    db_manager = DatabaseConnectionManager(
        app_name="db/ORMs/student_profile.py",
        database_name=os.environ.get("DB_NAME")
    )

    @classmethod
    def get_student_profile_by_user_id(cls, user_id: str):
        """Get student profile by user ID"""
        try:
            with cls.db_manager.get_session() as session:
                return session.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
        except SQLAlchemyError as e:
            logger.error(f"StudentProfileCRUD get_student_profile_by_user_id error: {e}")
            raise

    @classmethod
    def get_students_by_graduation_year(cls, graduation_year: int):
        """Get students by graduation year"""
        try:
            with cls.db_manager.get_session() as session:
                return session.query(StudentProfile).filter(StudentProfile.graduation_year == graduation_year).all()
        except SQLAlchemyError as e:
            logger.error(f"StudentProfileCRUD get_students_by_graduation_year error: {e}")
            raise

    @classmethod
    def create_student_profile(cls, profile_data: dict):
        """Create a new student profile"""
        try:
            with cls.db_manager.get_session() as session:
                profile = StudentProfile(**profile_data)
                session.add(profile)
                session.commit()
                return profile
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"StudentProfileCRUD create_student_profile error: {e}")
            raise

    @classmethod
    def update_student_profile(cls, user_id: str, update_data: dict):
        """Update student profile"""
        try:
            with cls.db_manager.get_session() as session:
                profile = session.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
                if not profile:
                    return None
                
                for key, value in update_data.items():
                    if hasattr(profile, key):
                        setattr(profile, key, value)
                
                session.commit()
                return profile
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"StudentProfileCRUD update_student_profile error: {e}")
            raise

    @classmethod
    def delete_student_profile(cls, user_id: str):
        """Delete student profile"""
        try:
            with cls.db_manager.get_session() as session:
                profile = session.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
                if not profile:
                    return None
                
                session.delete(profile)
                session.commit()
                return user_id
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"StudentProfileCRUD delete_student_profile error: {e}")
            raise