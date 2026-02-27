"""FastAPI 依赖项"""

from fastapi import Request
from typing import Optional, Any
from core.model_manager import ModelManager


def get_model_manager(request: Request) -> Optional[ModelManager]:
    """从 app.state 获取全局 ModelManager 实例"""
    return getattr(request.app.state, "model_manager", None)


def get_asr_system(request: Request) -> Optional[Any]:
    """从 app.state 获取 FireRedAsr2System 一站式识别实例"""
    return getattr(request.app.state, "asr_system", None)
