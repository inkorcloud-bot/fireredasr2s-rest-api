"""健康检查路由"""

from fastapi import APIRouter
from typing import Dict
from core.model_manager import ModelManager
from utils.response_builder import success_response

router = APIRouter(tags=["health"])
VERSION = "1.0.0"


@router.get("/api/v1/health")
async def health_check() -> Dict:
    """
    健康检查接口
    返回服务状态、版本、模型加载状态
    """
    try:
        manager = ModelManager()
        models_status = manager.get_status()
        all_loaded = all(status == 'loaded' for status in models_status.values())
        
        return success_response({
            "status": "healthy",
            "version": VERSION,
            "models_loaded": all_loaded,
            "models": models_status
        })
    except Exception as e:
        return success_response({
            "status": "unhealthy",
            "version": VERSION,
            "models_loaded": False,
            "error": str(e)
        })
