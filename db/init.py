"""Database initialization module for S2O API.

This module handles database table creation on application startup.
All models must be imported to register them with SQLAlchemy.
"""

from db.database import Base, engine


def init_db() -> None:
    """Initialize database by creating all tables.

    This function imports all models to ensure they are registered with
    SQLAlchemy's declarative base, then creates all defined tables.

    Should be called during application startup.
    """
    # Import all models to register them with Base
    # This ensures SQLAlchemy knows about all table definitions
    import models  # noqa: F401

    # Create all tables defined in models
    Base.metadata.create_all(bind=engine)
