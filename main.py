from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from controllers.review_controller import router as review_router
from controllers.customer_dashboard_controller import router as customer_dashboard_router

from controllers.auth_controller import router as auth_router
from controllers.restaurant_controller import router as restaurant_router
from controllers.category_controller import router as category_router
from controllers.menu_item_controller import router as menu_router
from controllers.table_controller import router as table_router
from controllers.qr_controller import router as qr_router
from controllers.guest import router as guest_router
from controllers.order_controller import router as order_router
from controllers.points_controller import router as point_router
from controllers.report_controller import router as report_router
from controllers.menu_analytics_controller import router as menu_analytics_router
from controllers.point_dashboard_controller import router as point_dashboard_router
from controllers.review_dashboard_controller import router as review_dashboard_router

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
    app.include_router(review_router)
    app.include_router(point_router)
    app.include_router(report_router)
    app.include_router(menu_analytics_router)
    app.include_router(customer_dashboard_router)
    app.include_router(point_dashboard_router)
    app.include_router(review_dashboard_router)

    return app


app = create_app()
