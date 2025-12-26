from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from controllers.auth_controller import router as auth_router
from controllers.restaurant_controller import router as restaurant_router
from controllers.category_controller import router as category_router
from controllers.menu_item_controller import router as menu_router

from db.init_db import init_db


def create_app() -> FastAPI:
    app = FastAPI(title="S2O API")

    # Serve static files (ảnh menu, v.v.)
    app.mount("/media", StaticFiles(directory="media"), name="media")
    app.mount("/media", StaticFiles(directory="media"), name="media")

    # Init database
    @app.on_event("startup")
    def on_startup():
        init_db()

    # Routers
    app.include_router(auth_router)
    app.include_router(restaurant_router)
    app.include_router(category_router)
    app.include_router(menu_router)

    return app


app = create_app()
