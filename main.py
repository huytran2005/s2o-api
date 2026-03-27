from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.middleware.cors import CORSMiddleware

def create_app() -> FastAPI:
    from controllers.auth_controller import router as auth_router
    from controllers.category_controller import router as category_router
    from controllers.customer_dashboard_controller import (
        router as customer_dashboard_router,
    )
    from controllers.guest import router as guest_router
    from controllers.health_controller import router as health_router
    from controllers.menu_analytics_controller import (
        router as menu_analytics_router,
    )
    from controllers.menu_item_controller import router as menu_router
    from controllers.order_controller import router as order_router
    from controllers.point_dashboard_controller import (
        router as point_dashboard_router,
    )
    from controllers.points_controller import router as point_router
    from controllers.report_controller import router as report_router
    from controllers.restaurant_controller import router as restaurant_router
    from controllers.review_controller import router as review_router
    from controllers.review_dashboard_controller import (
        router as review_dashboard_router,
    )
    from controllers.table_controller import router as table_router

    app = FastAPI(title="S2O API")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # Static files
    app.mount("/media", StaticFiles(directory="media"), name="media")

    # Routers
    app.include_router(auth_router)
    app.include_router(restaurant_router)
    app.include_router(table_router)
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
    app.include_router(health_router)

    Instrumentator(
        should_ignore_untemplated=True,
        excluded_handlers=["/metrics"]
    ).instrument(app).expose(app)

    return app


app = create_app()
