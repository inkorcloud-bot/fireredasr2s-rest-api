"""系统一站式识别路由"""

from fastapi import APIRouter, UploadFile, File, Form
from typing import Dict, Any
from core.model_manager import ModelManager
from core.processor import RequestProcessor
from utils.response_builder import success_response, error_response

router = APIRouter(tags=["system"])


@router.post("/api/v1/system/transcribe")
async def system_transcribe(
    audio: UploadFile = File(..., description="音频文件"),
    uttid: str = Form(None, description="话语ID"),
    enable_vad: bool = Form(True, description="启用VAD"),
    enable_lid: bool = Form(True, description="启用LID"),
    enable_punc: bool = Form(True, description="启用标点"),
    asr_type: str = Form("aed", description="ASR类型"),
    return_timestamp: bool = Form(False, description="返回时间戳")
) -> Dict[str, Any]:
    """
    一站式语音识别接口
    支持ASR、VAD、LID、标点预测的完整流程
    """
    try:
        manager = ModelManager()
        processor = RequestProcessor(manager, {})
        
        result = await processor.transcribe(
            audio_file=audio,
            uttid=uttid,
            enable_vad=enable_vad,
            enable_lid=enable_lid,
            enable_punc=enable_punc,
            asr_type=asr_type,
            return_timestamp=return_timestamp
        )
        
        return success_response(result, "识别成功")
    except Exception as e:
        return error_response(500, str(e))
