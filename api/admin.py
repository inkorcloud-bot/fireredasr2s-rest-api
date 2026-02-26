"""管理接口路由 - 配置、状态、重载"""

from fastapi import APIRouter, HTTPException
import psutil
from typing import Optional, List
from core.model_manager import ModelManager
from utils.config_loader import get_config
from utils.response_builder import success_response, error_response

router = APIRouter(tags=["admin"])


@router.get("/config")
async def get_admin_config():
    """获取当前配置（隐藏敏感信息）"""
    try:
        config = get_config()
        filtered = _filter_sensitive(config)
        return success_response(filtered, "配置获取成功")
    except Exception as e:
        return error_response(500, str(e))


@router.get("/status")
async def get_status():
    """获取服务状态和资源使用情况"""
    try:
        status = {
            "service": "running",
            "models": ModelManager().get_status(),
            "resources": {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent
            }
        }
        return success_response(status, "状态查询成功")
    except Exception as e:
        return error_response(500, str(e))


@router.post("/reload")
async def reload_models(modules: Optional[List[str]] = None):
    """热重载指定模块"""
    try:
        modules = modules or ["asr", "vad", "lid", "punc"]
        result = ModelManager().reload_modules(modules)
        return success_response(result, "模块重载完成")
    except Exception as e:
        return error_response(500, str(e))


def _filter_sensitive(config: dict) -> dict:
    """过滤敏感信息（密码、密钥等）"""
    sensitive_keys = ["password", "secret", "key", "token", "api_key"]
    if isinstance(config, dict):
        return {k: "***FILTERED***" if any(s in k.lower() for s in sensitive_keys) else _filter_sensitive(v)
                for k, v in config.items()}
    return config
