"""VAD 检测处理器"""

import os
import tempfile
from fastapi import UploadFile
from typing import Dict, Any
from utils.logger import get_logger
from utils.audio_validator import validate_audio_file
from utils.response_builder import error_response

logger = get_logger(__name__)


class VADProcessor:
    def __init__(self, model_manager, config: dict):
        self.model_manager = model_manager
        self.config = config
        logger.info("VADProcessor 初始化完成")

    async def detect(
        self,
        audio_file: UploadFile,
        speech_threshold: float = 0.4
    ) -> Dict[str, Any]:
        """VAD 检测"""
        vad_model = self.model_manager.get_model('vad')
        if not vad_model:
            return error_response(500, "VAD 模型未加载")
        
        try:
            audio_info = validate_audio_file(audio_file, self.config)
            await audio_file.seek(0)
            content = await audio_file.read()
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
                tmp.write(content)
                tmp_path = tmp.name
            
            try:
                result = vad_model.detect(tmp_path, speech_threshold=speech_threshold)
                result['audio_info'] = audio_info
                return result
            finally:
                os.unlink(tmp_path)
        except Exception as e:
            logger.error(f"VAD 检测失败: {e}")
            return error_response(500, str(e))

    async def aed_detect(self, audio_file: UploadFile) -> Dict[str, Any]:
        """音频事件检测"""
        vad_model = self.model_manager.get_model('vad')
        if not vad_model:
            return error_response(500, "VAD 模型未加载")
        
        try:
            audio_info = validate_audio_file(audio_file, self.config)
            await audio_file.seek(0)
            content = await audio_file.read()
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
                tmp.write(content)
                tmp_path = tmp.name
            
            try:
                result = vad_model.aed_detect(tmp_path)
                result['audio_info'] = audio_info
                return result
            finally:
                os.unlink(tmp_path)
        except Exception as e:
            logger.error(f"AED 检测失败: {e}")
            return error_response(500, str(e))
