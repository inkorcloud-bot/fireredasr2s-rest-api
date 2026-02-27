"""VAD 检测处理器"""

import os
from fastapi import UploadFile
from typing import Dict, Any
from utils.logger import get_logger
from utils.audio_validator import prepare_audio_for_asr
from utils.config_loader import get_config
from utils.response_builder import error_response

logger = get_logger(__name__)


class VADProcessor:
    def __init__(self, model_manager, config: dict):
        self.model_manager = model_manager
        self.config = config or get_config()
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
        
        wav_path = None
        try:
            audio_info, wav_path = prepare_audio_for_asr(audio_file, self.config)
            result = vad_model.detect(wav_path, speech_threshold=speech_threshold)
            result['audio_info'] = audio_info
            return result
        except Exception as e:
            logger.error(f"VAD 检测失败: {e}")
            return error_response(500, str(e))
        finally:
            if wav_path and os.path.exists(wav_path):
                try:
                    os.unlink(wav_path)
                except OSError:
                    pass

    async def aed_detect(self, audio_file: UploadFile) -> Dict[str, Any]:
        """音频事件检测。FireRedAsr2System 不包含 FireRedAed，统一加载时不可用"""
        vad_model = self.model_manager.get_model('vad')
        if not vad_model:
            return error_response(500, "VAD 模型未加载")

        if getattr(vad_model, "supports_aed", lambda: True)() is False:
            return error_response(503, "AED 功能在使用 FireRedAsr2System 统一加载时不可用")

        wav_path = None
        try:
            audio_info, wav_path = prepare_audio_for_asr(audio_file, self.config)
            result = vad_model.aed_detect(wav_path)
            result['audio_info'] = audio_info
            return result
        except Exception as e:
            logger.error(f"AED 检测失败: {e}")
            return error_response(500, str(e))
        finally:
            if wav_path and os.path.exists(wav_path):
                try:
                    os.unlink(wav_path)
                except OSError:
                    pass
