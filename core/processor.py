"""
请求处理器 - 一站式语音识别请求处理器
使用 FireRedAsr2System.process 执行 VAD→ASR→LID→Punc 完整流水线
"""

import asyncio
import os
import time
import uuid
from fastapi import UploadFile
from typing import Dict, Any, Optional
from utils.logger import get_logger
from utils.audio_validator import prepare_audio_for_asr
from utils.config_loader import get_config

logger = get_logger(__name__)


class RequestProcessor:
    """一站式语音识别请求处理器"""

    def __init__(self, model_manager, config: dict):
        """初始化请求处理器"""
        self.model_manager = model_manager
        self.config = config or get_config()

    async def transcribe(
        self,
        audio_file: UploadFile,
        asr_system,
        uttid: str = None,
        enable_vad: bool = True,
        enable_lid: bool = True,
        enable_punc: bool = True,
        asr_type: str = "aed",
        return_timestamp: bool = False,
    ) -> Dict[str, Any]:
        """
        一站式语音识别，调用 FireRedAsr2System.process 执行完整流水线。
        注意：enable_vad/enable_lid/enable_punc/asr_type/return_timestamp 由 config.yaml 决定，
        请求参数保留以兼容现有调用，当前实现以服务端配置为准。
        Returns: {
            'uttid': str, 'text': str, 'dur_s': float,
            'sentences': [...], 'vad_segments_ms': [...],
            'words': [...], 'processing_time_ms': int
        }
        """
        if not asr_system:
            raise ValueError("ASR System 未加载，请检查服务配置")

        start_time = time.time()
        uttid = uttid or str(uuid.uuid4())
        tmp_path = None

        try:
            audio_info, tmp_path = prepare_audio_for_asr(audio_file, self.config)
            logger.info(
                f"音频准备成功: {audio_info['filename']}, 时长: {audio_info['duration']:.2f}s"
                f"{', 已转码' if audio_info.get('transcoded') else ''}"
            )

            result = await asyncio.to_thread(asr_system.process, tmp_path, uttid)

            result.pop("wav_path", None)
            result["processing_time_ms"] = int((time.time() - start_time) * 1000)

            logger.info(f"识别完成: uttid={uttid}, 耗时={result['processing_time_ms']}ms")
            return result

        except Exception as e:
            logger.error(f"语音识别失败: {e}")
            raise
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except OSError as oe:
                    logger.warning(f"清理临时文件失败: {oe}")
