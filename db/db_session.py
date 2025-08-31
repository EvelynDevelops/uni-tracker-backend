from contextlib import contextmanager
from db.orm_db_manager import DatabaseConnectionManager
from fastapi import Depends

# You may want to use a singleton or global manager
db_manager = DatabaseConnectionManager(app_name="db/db_session.py")

@contextmanager
def db_session():
    """
    Context manager for SQLAlchemy session with automatic commit/rollback/close.
    Usage:
        with db_session() as session:
            # do db operations
    """
    session = db_manager.get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def get_db():
    """
    FastAPI dependency that provides a SQLAlchemy session and ensures it is closed after the request.
    Usage:
        def some_api(db: Session = Depends(get_db)):
            ...
    """
    session = db_manager.get_session()
    try:
        yield session
    finally:
        session.close()
