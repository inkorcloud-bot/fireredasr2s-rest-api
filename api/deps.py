"""FastAPI 依赖项"""

from fastapi import Request
from typing import Optional
from core.model_manager import ModelManager


def get_model_manager(request: Request) -> Optional[ModelManager]:
    """从 app.state 获取全局 ModelManager 实例"""
    return getattr(request.app.state, "model_manager", None)
