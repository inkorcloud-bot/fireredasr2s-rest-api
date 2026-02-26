"""
音频验证工具模块
"""

import wave
import os
import tempfile
from fastapi import UploadFile
from typing import Dict, Any
from .logger import get_logger
from .error_codes import ErrorCode, ERROR_MESSAGES

logger = get_logger(__name__)


def validate_audio_file(
    file: UploadFile,
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    验证音频文件，返回音频元信息
    Raises: ValueError with error_code
    """
    processing_config = config.get('processing', {})
    max_file_size = processing_config.get('max_file_size', 52428800)
    max_duration = processing_config.get('max_audio_duration', 60)
    supported_formats = processing_config.get('supported_formats', ['wav'])
    
    filename = file.filename or ""
    file_ext = os.path.splitext(filename)[1].lower().lstrip('.')
    
    # 验证格式
    if file_ext not in supported_formats:
        error = ValueError(ERROR_MESSAGES[ErrorCode.INVALID_AUDIO_FORMAT])
        error.error_code = ErrorCode.INVALID_AUDIO_FORMAT
        raise error
    
    # 验证文件大小
    content = file.file.read()
    file_size = len(content)
    if file_size > max_file_size:
        error = ValueError(ERROR_MESSAGES[ErrorCode.AUDIO_FILE_TOO_LARGE])
        error.error_code = ErrorCode.AUDIO_FILE_TOO_LARGE
        raise error
    
    # 临时保存文件以读取音频信息
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        duration, sample_rate, channels, sample_width = _read_wav_info(tmp_path)
        
        # 验证时长
        if duration > max_duration:
            error = ValueError(ERROR_MESSAGES[ErrorCode.AUDIO_DURATION_EXCEEDED])
            error.error_code = ErrorCode.AUDIO_DURATION_EXCEEDED
            raise error
        
        return {
            'filename': filename,
            'size': file_size,
            'duration': duration,
            'sample_rate': sample_rate,
            'channels': channels,
            'sample_width': sample_width,
            'format': file_ext
        }
    finally:
        os.unlink(tmp_path)


def get_audio_duration(file_path: str) -> float:
    """获取音频文件时长（秒）"""
    duration, *_ = _read_wav_info(file_path)
    return duration


def _read_wav_info(file_path: str) -> tuple:
    """读取 WAV 文件信息"""
    try:
        with wave.open(file_path, 'rb') as wav:
            frames = wav.getnframes()
            rate = wav.getframerate()
            duration = frames / float(rate)
            return duration, rate, wav.getnchannels(), wav.getsampwidth()
    except Exception as e:
        logger.error(f"读取 WAV 文件失败: {e}")
        raise ValueError(ERROR_MESSAGES[ErrorCode.INVALID_AUDIO_FORMAT])
