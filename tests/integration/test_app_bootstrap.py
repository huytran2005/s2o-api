from main import create_app


def test_create_app_registers_core_routes():
    app = create_app()
    route_paths = {route.path for route in app.routes}

    assert "/health" in route_paths
    assert "/auth/login" in route_paths
    assert "/auth/register" in route_paths
    assert "/metrics" in route_paths
