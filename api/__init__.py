"""API 路由聚合"""

from fastapi import FastAPI
from .health import router as health_router
from .system import router as system_router
from .admin import router as admin_router


def register_routers(app: FastAPI) -> None:
    """注册所有路由到 FastAPI 应用"""
    app.include_router(health_router)
    app.include_router(system_router)
    app.include_router(admin_router)
