"""LID 模块路由"""

from typing import Optional
from fastapi import APIRouter, UploadFile, File, Depends
from core.model_manager import ModelManager
from core.lid_processor import LIDProcessor
from api.deps import get_model_manager
from utils.response_builder import success_response, error_response

router = APIRouter(prefix="/api/v1/modules/lid", tags=["LID"])


@router.post("/detect")
async def lid_detect(
    audio_file: UploadFile = File(...),
    manager: Optional[ModelManager] = Depends(get_model_manager)
):
    try:
        if not manager:
            return error_response(500, "服务未就绪，模型管理器未初始化")
        processor = LIDProcessor(manager, {})
        return success_response(await processor.detect(audio_file))
    except Exception as e:
        return error_response(500, str(e))
