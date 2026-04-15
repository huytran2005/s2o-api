from main import create_app
from db.database import Base, engine


def test_create_app_registers_core_routes():
    app = create_app()
    route_paths = {route.path for route in app.routes}

    assert "/health" in route_paths
    assert "/auth/login" in route_paths
    assert "/auth/register" in route_paths
    assert "/metrics" in route_paths


def test_app_startup_creates_db_tables(mocker):
    # Mock Base.metadata.create_all to prevent actual table creation during test
    create_all_mock = mocker.patch("db.database.Base.metadata.create_all")

    # Create the app, which will trigger the on_startup event
    create_app()

    # Assert that create_all was called
    create_all_mock.assert_called_once_with(bind=engine)

