from fastapi import FastAPI

from controllers.auth_controller import router as auth_router


def create_app() -> FastAPI:
    """Create FastAPI application instance without side effects (no DB init here)."""
    app = FastAPI(title="S2O API")
    app.include_router(auth_router)
    return app


app = create_app()



