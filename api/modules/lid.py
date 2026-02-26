"""LID 模块路由"""

from fastapi import APIRouter, UploadFile, File
from core.lid_processor import LIDProcessor
from utils.response_builder import success_response, error_response

router = APIRouter(prefix="/api/v1/modules/lid", tags=["LID"])


@router.post("/detect")
async def lid_detect(audio_file: UploadFile = File(...)):
    try:
        return success_response(await LIDProcessor.detect(audio_file))
    except Exception as e:
        return error_response(500, str(e))
