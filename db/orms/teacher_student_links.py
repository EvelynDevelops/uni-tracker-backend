import os
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from db.orm_db_manager import DatabaseConnectionManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()

class TeacherStudentLink(Base):
    __tablename__ = "teacher_student_links"

    teacher_user_id = Column(UUID(as_uuid=True), ForeignKey('profiles.user_id'), primary_key=True)
    student_user_id = Column(UUID(as_uuid=True), ForeignKey('profiles.user_id'), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    teacher = relationship("Profile", foreign_keys=[teacher_user_id])
    student = relationship("Profile", foreign_keys=[student_user_id])

    def __repr__(self):
        return f"<TeacherStudentLink(teacher_user_id={self.teacher_user_id}, student_user_id={self.student_user_id})>"


class TeacherStudentLinkCRUD:
    db_manager = DatabaseConnectionManager(
        app_name="db/ORMs/teacher_student_links.py",
        database_name=os.environ.get("DB_NAME")
    )

    @classmethod
    def get_teacher_links_by_teacher_id(cls, teacher_user_id: str):
        """Get all teacher links for a teacher"""
        try:
            with cls.db_manager.get_session() as session:
                return session.query(TeacherStudentLink).filter(TeacherStudentLink.teacher_user_id == teacher_user_id).all()
        except SQLAlchemyError as e:
            logger.error(f"TeacherStudentLinkCRUD get_teacher_links_by_teacher_id error: {e}")
            raise

    @classmethod
    def get_teacher_links_by_student_id(cls, student_user_id: str):
        """Get all teacher links for a student"""
        try:
            with cls.db_manager.get_session() as session:
                return session.query(TeacherStudentLink).filter(TeacherStudentLink.student_user_id == student_user_id).all()
        except SQLAlchemyError as e:
            logger.error(f"TeacherStudentLinkCRUD get_teacher_links_by_student_id error: {e}")
            raise

    @classmethod
    def create_teacher_link(cls, teacher_user_id: str, student_user_id: str):
        """Create a new teacher link"""
        try:
            with cls.db_manager.get_session() as session:
                teacher_link = TeacherStudentLink(
                    teacher_user_id=teacher_user_id,
                    student_user_id=student_user_id
                )
                session.add(teacher_link)
                session.commit()
                return teacher_link
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"TeacherStudentLinkCRUD create_teacher_link error: {e}")
            raise

    @classmethod
    def delete_teacher_link(cls, teacher_user_id: str, student_user_id: str):
        """Delete teacher link"""
        try:
            with cls.db_manager.get_session() as session:
                teacher_link = session.query(TeacherStudentLink).filter(
                    TeacherStudentLink.teacher_user_id == teacher_user_id,
                    TeacherStudentLink.student_user_id == student_user_id
                ).first()
                
                if not teacher_link:
                    return None
                
                session.delete(teacher_link)
                session.commit()
                return teacher_link
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"TeacherStudentLinkCRUD delete_teacher_link error: {e}")
            raise

    @classmethod
    def check_teacher_link_exists(cls, teacher_user_id: str, student_user_id: str):
        """Check if teacher link exists"""
        try:
            with cls.db_manager.get_session() as session:
                return session.query(TeacherStudentLink).filter(
                    TeacherStudentLink.teacher_user_id == teacher_user_id,
                    TeacherStudentLink.student_user_id == student_user_id
                ).first() is not None
        except SQLAlchemyError as e:
            logger.error(f"TeacherStudentLinkCRUD check_teacher_link_exists error: {e}")
            raise
