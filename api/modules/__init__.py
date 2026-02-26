"""模块路由聚合"""

from fastapi import FastAPI
from .asr import router as asr_router


def register_module_routers(app: FastAPI) -> None:
    """注册模块路由到 FastAPI 应用"""
    app.include_router(asr_router)
