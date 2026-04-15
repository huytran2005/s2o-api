"""Tests for database initialization."""

import pytest
from unittest.mock import patch, MagicMock, call

from db.init import init_db


class TestInitDb:
    """Test database initialization function."""

    def test_init_db_calls_create_all(self):
        """Test that init_db calls Base.metadata.create_all with correct engine."""
        with patch("db.init.Base.metadata.create_all") as mock_create_all:
            init_db()
            mock_create_all.assert_called_once()
            # Verify it was called with bind parameter
            call_args = mock_create_all.call_args
            assert "bind" in call_args.kwargs

    def test_init_db_imports_models(self):
        """Test that init_db imports all models without errors."""
        # This should not raise any exceptions
        try:
            init_db()
        except Exception as e:
            pytest.fail(f"init_db raised unexpected exception: {e}")

    def test_init_db_idempotent(self):
        """Test that init_db can be called multiple times safely."""
        # Calling twice should not raise errors
        with patch("db.init.Base.metadata.create_all"):
            init_db()
            init_db()  # Should complete without error

    def test_init_db_creates_tables_in_real_db(self):
        """Integration test: verify init_db actually creates tables."""
        from db.database import Base, engine
        from sqlalchemy import inspect

        # Clean up any existing tables first
        Base.metadata.drop_all(bind=engine)

        # Call init_db
        init_db()

        # Verify tables were created
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        # Should have created multiple tables from models
        assert len(tables) > 0, "No tables were created by init_db"

        # Verify some expected tables exist
        assert "app_user" in tables or "tenant" in tables, (
            "Expected model tables not found in database"
        )

