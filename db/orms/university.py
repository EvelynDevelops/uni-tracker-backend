import os
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, String, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from db.orm_db_manager import DatabaseConnectionManager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()

class University(Base):
    __tablename__ = "universities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    country_code = Column(String(2), nullable=False)
    state_province = Column(Text, nullable=True)
    city = Column(Text, nullable=True)
    website = Column(Text, nullable=True)
    domain = Column(String, unique=True, nullable=True)
    aliases = Column(ARRAY(String), default=[])
    external_ids = Column(JSONB, default={})
    apply_portals = Column(JSONB, default=[])
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<University(id={self.id}, name='{self.name}', country_code='{self.country_code}')>"


class UniversityCRUD:
    db_manager = DatabaseConnectionManager(
        app_name="db/ORMs/university.py",
        database_name=os.environ.get("DB_NAME")
    )

    @classmethod
    def fetch_university_ids(cls):
        """
        Fetches all university id values from the database using ORM.
        :return: List[str] - university ids ordered as in the database.
        """
        try:
            with cls.db_manager.get_session() as session:
                university_ids = session.query(University.id).order_by(University.id).all()
                return [str(row[0]) for row in university_ids]
        except SQLAlchemyError as e:
            logger.error(f"UniversityCRUD fetch_university_ids error: {e}")
            raise

    @classmethod
    def add_university(cls, university_data):
        """Insert a new university."""
        try:
            with cls.db_manager.get_session() as session:
                new_university = University(**university_data)
                session.add(new_university)
                session.commit()
                return new_university
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"UniversityCRUD add_university error: {e}")
            raise

    @classmethod
    def get_university_by_id(cls, university_id):
        """Fetch a university by id."""
        try:
            with cls.db_manager.get_session() as session:
                return session.query(University).filter(University.id == university_id).first()
        except SQLAlchemyError as e:
            logger.error(f"UniversityCRUD get_university_by_id error: {e}")
            raise

    @classmethod
    def get_university_by_domain(cls, domain):
        """Fetch a university by domain."""
        try:
            with cls.db_manager.get_session() as session:
                return session.query(University).filter(University.domain == domain).first()
        except SQLAlchemyError as e:
            logger.error(f"UniversityCRUD get_university_by_domain error: {e}")
            raise

    @classmethod
    def get_university_by_name_and_country(cls, name, country_code):
        """Fetch a university by name and country code (case insensitive)."""
        try:
            with cls.db_manager.get_session() as session:
                return session.query(University).filter(
                    func.lower(University.name) == func.lower(name),
                    University.country_code == country_code
                ).first()
        except SQLAlchemyError as e:
            logger.error(f"UniversityCRUD get_university_by_name_and_country error: {e}")
            raise

    @classmethod
    def get_universities_by_ids(cls, university_ids):
        """Fetch multiple universities by a list of university ids."""
        try:
            if isinstance(university_ids, list):
                university_ids = tuple(university_ids)

            with cls.db_manager.get_session() as session:
                universities = (
                    session.query(University.id, University.name, University.country_code, University.domain)
                    .filter(University.id.in_(university_ids))
                    .all()
                )

                universities_dict = {
                    str(u.id): {
                        "name": u.name, 
                        "country_code": u.country_code, 
                        "domain": u.domain
                    } for u in universities
                }
                return universities_dict

        except SQLAlchemyError as e:
            logger.error(f"UniversityCRUD get_universities_by_ids error: {e}")
            raise

    @classmethod
    def get_universities_by_country(cls, country_code):
        """Fetch all universities by country code."""
        try:
            with cls.db_manager.get_session() as session:
                return session.query(University).filter(University.country_code == country_code).all()
        except SQLAlchemyError as e:
            logger.error(f"UniversityCRUD get_universities_by_country error: {e}")
            raise

    @classmethod
    def get_universities_by_type(cls, university_type=None):
        """Fetch all universities, optionally filtered by type (placeholder for future use)."""
        try:
            with cls.db_manager.get_session() as session:
                if university_type:
                    # Placeholder for future filtering logic
                    return session.query(University).filter(University.name.contains(university_type)).all()
                else:
                    return session.query(University).all()
        except SQLAlchemyError as e:
            logger.error(f"UniversityCRUD get_universities_by_type error: {e}")
            raise

    @classmethod
    def get_all_universities(cls):
        """Fetch all universities excluding timestamps, ensuring name is not null or empty."""
        try:
            with cls.db_manager.get_session() as session:
                universities = session.query(
                    University.id,
                    University.name,
                    University.country_code,
                    University.state_province,
                    University.city,
                    University.website,
                    University.domain,
                    University.aliases,
                    University.external_ids,
                    University.apply_portals
                ).filter(
                    University.name.isnot(None),
                    University.name != ""
                ).all()
                
                return universities
        except SQLAlchemyError as e:
            logger.error(f"UniversityCRUD get_all_universities error: {e}")
            raise

    @classmethod
    def update_university(cls, university_id, update_data):
        """Update a university's details."""
        try:
            with cls.db_manager.get_session() as session:
                university = session.query(University).filter(University.id == university_id).first()
                if not university:
                    return None
                
                for key, value in update_data.items():
                    if hasattr(university, key):
                        setattr(university, key, value)
                
                university.updated_at = datetime.utcnow()
                session.commit()
                return university
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"UniversityCRUD update_university error: {e}")
            raise

    @classmethod
    def delete_university(cls, university_id):
        """Delete a university by id."""
        try:
            with cls.db_manager.get_session() as session:
                university = session.query(University).filter(University.id == university_id).first()
                if not university:
                    return None
                
                session.delete(university)
                session.commit()
                return university_id
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"UniversityCRUD delete_university error: {e}")
            raise

    @classmethod
    def create_or_update_university(cls, university_data):
        """
        Create a new university or update existing one based on domain or name+country_code.
        This is the main method for upsert operations.
        """
        try:
            with cls.db_manager.get_session() as session:
                domain = university_data.get('domain')
                
                if domain:
                    # Try to find by domain first
                    existing = session.query(University).filter(University.domain == domain).first()
                else:
                    # Fallback to name + country_code
                    name = university_data.get('name')
                    country_code = university_data.get('country_code')
                    if name and country_code:
                        existing = session.query(University).filter(
                            func.lower(University.name) == func.lower(name),
                            University.country_code == country_code
                        ).first()
                    else:
                        existing = None

                if existing:
                    # Update existing record
                    for key, value in university_data.items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)
                    existing.updated_at = datetime.utcnow()
                    session.commit()
                    return existing
                else:
                    # Create new record
                    new_university = University(**university_data)
                    session.add(new_university)
                    session.commit()
                    return new_university
                    
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"UniversityCRUD create_or_update_university error: {e}")
            raise

    @classmethod
    def search_universities(cls, search_term, limit=10):
        """Search universities by name (case insensitive)."""
        try:
            with cls.db_manager.get_session() as session:
                universities = session.query(University).filter(
                    func.lower(University.name).contains(func.lower(search_term))
                ).limit(limit).all()
                return universities
        except SQLAlchemyError as e:
            logger.error(f"UniversityCRUD search_universities error: {e}")
            raise
