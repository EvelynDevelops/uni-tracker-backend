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

class ParentLink(Base):
    __tablename__ = "parent_links"

    parent_user_id = Column(UUID(as_uuid=True), ForeignKey('profiles.user_id'), primary_key=True)
    student_user_id = Column(UUID(as_uuid=True), ForeignKey('profiles.user_id'), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    parent = relationship("Profile", foreign_keys=[parent_user_id])
    student = relationship("Profile", foreign_keys=[student_user_id])

    def __repr__(self):
        return f"<ParentLink(parent_user_id={self.parent_user_id}, student_user_id={self.student_user_id})>"


class ParentLinkCRUD:
    db_manager = DatabaseConnectionManager(
        app_name="db/ORMs/parent_links.py",
        database_name=os.environ.get("DB_NAME")
    )

    @classmethod
    def get_parent_links_by_parent_id(cls, parent_user_id: str):
        """Get all parent links for a parent"""
        try:
            with cls.db_manager.get_session() as session:
                return session.query(ParentLink).filter(ParentLink.parent_user_id == parent_user_id).all()
        except SQLAlchemyError as e:
            logger.error(f"ParentLinkCRUD get_parent_links_by_parent_id error: {e}")
            raise

    @classmethod
    def get_parent_links_by_student_id(cls, student_user_id: str):
        """Get all parent links for a student"""
        try:
            with cls.db_manager.get_session() as session:
                return session.query(ParentLink).filter(ParentLink.student_user_id == student_user_id).all()
        except SQLAlchemyError as e:
            logger.error(f"ParentLinkCRUD get_parent_links_by_student_id error: {e}")
            raise

    @classmethod
    def create_parent_link(cls, parent_user_id: str, student_user_id: str):
        """Create a new parent link"""
        try:
            with cls.db_manager.get_session() as session:
                parent_link = ParentLink(
                    parent_user_id=parent_user_id,
                    student_user_id=student_user_id
                )
                session.add(parent_link)
                session.commit()
                return parent_link
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"ParentLinkCRUD create_parent_link error: {e}")
            raise

    @classmethod
    def delete_parent_link(cls, parent_user_id: str, student_user_id: str):
        """Delete parent link"""
        try:
            with cls.db_manager.get_session() as session:
                parent_link = session.query(ParentLink).filter(
                    ParentLink.parent_user_id == parent_user_id,
                    ParentLink.student_user_id == student_user_id
                ).first()
                
                if not parent_link:
                    return None
                
                session.delete(parent_link)
                session.commit()
                return parent_link
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"ParentLinkCRUD delete_parent_link error: {e}")
            raise

    @classmethod
    def check_parent_link_exists(cls, parent_user_id: str, student_user_id: str):
        """Check if parent link exists"""
        try:
            with cls.db_manager.get_session() as session:
                return session.query(ParentLink).filter(
                    ParentLink.parent_user_id == parent_user_id,
                    ParentLink.student_user_id == student_user_id
                ).first() is not None
        except SQLAlchemyError as e:
            logger.error(f"ParentLinkCRUD check_parent_link_exists error: {e}")
            raise
