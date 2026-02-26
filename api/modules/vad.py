"""VAD 模块路由"""

from fastapi import APIRouter, UploadFile, File, WebSocket, WebSocketDisconnect
from ...core.vad_processor import VADProcessor
from ...utils.response_builder import success_response, error_response

router = APIRouter(prefix="/api/v1/modules/vad", tags=["VAD"])


@router.post("/detect")
async def vad_detect(audio_file: UploadFile = File(...), speech_threshold: float = 0.4):
    try:
        return success_response(await VADProcessor.detect(audio_file, speech_threshold))
    except Exception as e:
        return error_response(500, str(e))


@router.post("/aed")
async def aed_detect(audio_file: UploadFile = File(...)):
    try:
        return success_response(await VADProcessor.aed_detect(audio_file))
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
