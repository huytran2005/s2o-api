from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from controllers.auth_controller import router as auth_router
from controllers.restaurant_controller import router as restaurant_router
from db.init_db import init_db


def create_app() -> FastAPI:
    app = FastAPI(title="S2O API")

    app.mount("/media", StaticFiles(directory="media"), name="media")

    @app.on_event("startup")
    def on_startup():
        init_db()

    app.include_router(auth_router)
    app.include_router(restaurant_router)

    return app


app = create_app()
