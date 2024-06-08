import logging
from importlib import metadata
from pathlib import Path

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import UJSONResponse
from fastapi.staticfiles import StaticFiles
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sqladmin import Admin
from sqlalchemy.ext.asyncio import create_async_engine

from iot_backend.admin import (
    AlertView,
    DeviceView,
    GroupView,
    OrganizationView,
    TagView,
    UserView,
    authentication_backend,
)
from iot_backend.logging import configure_logging
from iot_backend.settings import settings
from iot_backend.web.api.router import api_router
from iot_backend.web.lifetime import register_shutdown_event, register_startup_event

APP_ROOT = Path(__file__).parent.parent


def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    configure_logging()
    if settings.sentry_dsn:
        # Enables sentry integration.
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            traces_sample_rate=settings.sentry_sample_rate,
            environment=settings.environment,
            integrations=[
                FastApiIntegration(transaction_style="endpoint"),
                LoggingIntegration(
                    level=logging.getLevelName(
                        settings.log_level.value,
                    ),
                    event_level=logging.ERROR,
                ),
                SqlalchemyIntegration(),
            ],
        )
    app = FastAPI(
        title="iot_backend",
        version=metadata.version("iot_backend"),
        docs_url=None,
        redoc_url=None,
        openapi_url="/api/openapi.json",
        default_response_class=UJSONResponse,
    )
    # Adds CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Replace "*" with your desired origins
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # Adds startup and shutdown events.
    register_startup_event(app)
    register_shutdown_event(app)

    # Main router for the API.
    app.include_router(router=api_router, prefix="/api")
    # Adds static directory.
    # This directory is used to access swagger files.
    app.mount(
        "/static",
        StaticFiles(directory=APP_ROOT / "static"),
        name="static",
    )

    admin = Admin(
        app=app,
        authentication_backend=authentication_backend,
        engine=create_async_engine(str(settings.db_url), echo=settings.db_echo),
        debug=True,
        # templates_dir="app/admin/templates"
    )
    admin.add_view(UserView)
    admin.add_view(OrganizationView)
    admin.add_view(GroupView)
    admin.add_view(DeviceView)
    admin.add_view(AlertView)
    admin.add_view(TagView)
    return app
