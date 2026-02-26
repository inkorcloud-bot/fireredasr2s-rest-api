"""ASR模块路由 - 批量转录和信息查询"""

from fastapi import APIRouter, UploadFile, File, Form, Depends
from typing import Dict, Any, Optional
from core.model_manager import ModelManager
from core.asr_processor import ASRProcessor
from api.deps import get_model_manager
from utils.audio_converter import SUPPORTED_AUDIO_EXTENSIONS
from utils.response_builder import success_response, error_response

router = APIRouter(tags=["ASR"])
VERSION = "1.0.0"


@router.post("/asr/transcribe")
async def asr_batch_transcribe(
    audios: list[UploadFile] = File(..., description="多个音频文件"),
    asr_type: str = Form("aed", description="ASR类型"),
    beam_size: int = Form(3, description="beam size"),
    return_timestamp: bool = Form(False, description="返回时间戳"),
    manager: Optional[ModelManager] = Depends(get_model_manager)
) -> Dict[str, Any]:
    """
    ASR批量转录接口
    支持同时处理多个音频文件
    """
    try:
        if not manager:
            return error_response(500, "服务未就绪，模型管理器未初始化")
        processor = ASRProcessor(manager, {})
        
        result = await processor.batch_transcribe(
            audio_files=audios,
            asr_type=asr_type,
            beam_size=beam_size,
            return_timestamp=return_timestamp
        )
        
        return success_response(result, "批量转录完成")
    except Exception as e:
        return error_response(500, str(e))


@router.get("/asr/info")
async def asr_info(manager: Optional[ModelManager] = Depends(get_model_manager)) -> Dict[str, Any]:
    """
    ASR模块信息接口
    返回ASR模块的版本和状态信息
    """
    try:
        if not manager:
            return error_response(500, "服务未就绪，模型管理器未初始化")
        model = manager.get_model('asr')
        
        info = {
            "version": VERSION,
            "loaded": model is not None,
            "type": "FireRedASR2S",
            "supported_formats": sorted(SUPPORTED_AUDIO_EXTENSIONS),
            "features": ["batch_transcribe", "timestamp", "beam_search", "auto_transcode"]
        }
        
        return success_response(info, "ASR信息查询成功")
    except Exception as e:
        return error_response(500, str(e))
