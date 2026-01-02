from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from controllers.auth_controller import router as auth_router
from controllers.restaurant_controller import router as restaurant_router
from controllers.category_controller import router as category_router
from controllers.menu_item_controller import router as menu_router
from controllers.table_controller import router as table_router
from controllers.qr_controller import router as qr_router
from controllers.guest import router as guest_router
from controllers.order_controller import router as order_router  # ✅ THÊM

from db.init_db import init_db


def create_app() -> FastAPI:
    app = FastAPI(title="S2O API")

    # Static files
    app.mount("/media", StaticFiles(directory="media"), name="media")

    @app.on_event("startup")
    def on_startup():
        init_db()

    # Routers
    app.include_router(auth_router)
    app.include_router(restaurant_router)
    app.include_router(table_router)
    app.include_router(qr_router)
    app.include_router(guest_router)
    app.include_router(category_router)
    app.include_router(menu_router)
    app.include_router(order_router)

    return app


app = create_app()
