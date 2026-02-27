"""系统一站式识别路由

使用 FireRedAsr2System.process 执行 VAD→ASR→LID→Punc 完整流水线。
enable_vad/enable_lid/enable_punc/asr_type/return_timestamp 由 config.yaml 决定，
请求参数保留以兼容现有调用。
"""

from fastapi import APIRouter, UploadFile, File, Form, Depends
from typing import Dict, Any, Optional
from core.model_manager import ModelManager
from core.processor import RequestProcessor
from api.deps import get_model_manager, get_asr_system
from utils.response_builder import success_response, error_response

router = APIRouter(tags=["system"])


@router.post("/system/transcribe")
async def system_transcribe(
    audio: UploadFile = File(..., description="音频文件"),
    uttid: str = Form(None, description="话语ID"),
    enable_vad: bool = Form(True, description="启用VAD（以 config 为准）"),
    enable_lid: bool = Form(True, description="启用LID（以 config 为准）"),
    enable_punc: bool = Form(True, description="启用标点（以 config 为准）"),
    asr_type: str = Form("aed", description="ASR类型（以 config 为准）"),
    return_timestamp: bool = Form(False, description="返回时间戳（以 config 为准）"),
    manager: Optional[ModelManager] = Depends(get_model_manager),
    asr_system: Optional[Any] = Depends(get_asr_system),
) -> Dict[str, Any]:
    """
    一站式语音识别接口
    调用 FireRedAsr2System.process 执行 ASR、VAD、LID、标点预测的完整流水线
    """
    try:
        if not asr_system:
            return error_response(500, "ASR System 未加载，请检查 config 中 asr.enabled")
        processor = RequestProcessor(manager, {})
        result = await processor.transcribe(
            audio_file=audio,
            asr_system=asr_system,
            uttid=uttid,
            enable_vad=enable_vad,
            enable_lid=enable_lid,
            enable_punc=enable_punc,
            asr_type=asr_type,
            return_timestamp=return_timestamp,
        )
        return success_response(result, "识别成功")
    except Exception as e:
        return error_response(500, str(e))
