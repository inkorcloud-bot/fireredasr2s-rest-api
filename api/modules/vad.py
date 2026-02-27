"""VAD 模块路由"""

from typing import Optional
from fastapi import APIRouter, UploadFile, File, WebSocket, WebSocketDisconnect, Depends
from core.model_manager import ModelManager
from core.vad_processor import VADProcessor
from api.deps import get_model_manager
from utils.response_builder import success_response, error_response

router = APIRouter(prefix="/api/v1/modules/vad", tags=["VAD"])


@router.post("/detect")
async def vad_detect(
    audio_file: UploadFile = File(...),
    speech_threshold: float = 0.4,
    manager: Optional[ModelManager] = Depends(get_model_manager)
):
    try:
        if not manager:
            return error_response(500, "服务未就绪，模型管理器未初始化")
        processor = VADProcessor(manager, {})
        return success_response(await processor.detect(audio_file, speech_threshold))
    except Exception as e:
        return error_response(500, str(e))


@router.post("/aed")
async def aed_detect(
    audio_file: UploadFile = File(...),
    manager: Optional[ModelManager] = Depends(get_model_manager)
):
    try:
        if not manager:
            return error_response(500, "服务未就绪，模型管理器未初始化")
        processor = VADProcessor(manager, {})
        return success_response(await processor.aed_detect(audio_file))
    except Exception as e:
        return error_response(500, str(e))


@router.websocket("/stream")
async def vad_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_bytes()
            await websocket.send_json({"is_speech": len(data) > 1000})
    except WebSocketDisconnect:
        pass
