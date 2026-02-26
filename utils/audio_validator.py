"""
音频验证工具模块
支持多种音频格式，非 WAV 格式将自动转码为 16kHz 16-bit mono PCM WAV
"""

import wave
import os
import tempfile
from fastapi import UploadFile
from typing import Dict, Any, Tuple
from .logger import get_logger
from .error_codes import ErrorCode, ERROR_MESSAGES
from .audio_converter import (
    transcode_to_wav,
    get_audio_duration_ffprobe,
    SUPPORTED_AUDIO_EXTENSIONS,
    TARGET_SAMPLE_RATE,
    TARGET_CHANNELS,
    TARGET_SAMPLE_WIDTH,
)

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
    
    filename = file.filename or ""
    file_ext = os.path.splitext(filename)[1].lower().lstrip('.') or 'wav'
    
    # 验证格式（使用 FFmpeg 支持的扩展名列表）
    if file_ext not in SUPPORTED_AUDIO_EXTENSIONS:
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


def prepare_audio_for_asr(
    file: UploadFile,
    config: Dict[str, Any]
) -> Tuple[Dict[str, Any], str]:
    """
    验证音频并准备为 ASR 可用的 16kHz 16-bit mono PCM WAV。
    非 WAV 或格式不符合的音频将通过 ffmpeg 自动转码。
    
    Returns:
        (audio_info, wav_path): 元信息字典和 WAV 文件路径
        调用方需在完成后 os.unlink(wav_path) 清理临时文件
    
    Raises:
        ValueError with error_code
    """
    from .config_loader import get_config
    cfg = config if config else get_config()
    processing_config = cfg.get('processing', {})
    max_file_size = processing_config.get('max_file_size', 52428800)
    max_duration = processing_config.get('max_audio_duration', 60)
    
    filename = file.filename or ""
    file_ext = os.path.splitext(filename)[1].lower().lstrip('.') or 'wav'
    logger.debug(f"音频文件: filename={filename!r}, file_ext={file_ext!r}")
    
    if file_ext not in SUPPORTED_AUDIO_EXTENSIONS:
        logger.warning(f"不支持的音频格式: 文件={filename!r}, 扩展名={file_ext!r}")
        error = ValueError(ERROR_MESSAGES[ErrorCode.INVALID_AUDIO_FORMAT])
        error.error_code = ErrorCode.INVALID_AUDIO_FORMAT
        raise error
    
    content = file.file.read()
    file_size = len(content)
    if file_size > max_file_size:
        error = ValueError(ERROR_MESSAGES[ErrorCode.AUDIO_FILE_TOO_LARGE])
        error.error_code = ErrorCode.AUDIO_FILE_TOO_LARGE
        raise error
    
    # 保存到临时文件（保留原始扩展名以便 ffmpeg 识别）
    suffix = f'.{file_ext}' if file_ext else '.bin'
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(content)
        input_path = tmp.name
    
    output_path = None
    try:
        # 获取时长
        if file_ext == 'wav':
            try:
                duration, sample_rate, channels, sample_width = _read_wav_info(input_path)
            except ValueError:
                # WAV 解析失败，尝试 ffmpeg 转码
                duration = get_audio_duration_ffprobe(input_path)
                sample_rate, channels, sample_width = 0, 0, 0
        else:
            duration = get_audio_duration_ffprobe(input_path)
            sample_rate, channels, sample_width = TARGET_SAMPLE_RATE, TARGET_CHANNELS, TARGET_SAMPLE_WIDTH
        
        if duration > max_duration:
            os.unlink(input_path)
            error = ValueError(ERROR_MESSAGES[ErrorCode.AUDIO_DURATION_EXCEEDED])
            error.error_code = ErrorCode.AUDIO_DURATION_EXCEEDED
            raise error
        
        # 判断是否需要转码：非标准 WAV 或 WAV 格式/采样率/声道不符合要求
        need_transcode = (
            file_ext not in ('wav', 'wave') or
            (sample_rate != TARGET_SAMPLE_RATE or
             channels != TARGET_CHANNELS or
             sample_width != TARGET_SAMPLE_WIDTH)
        )
        
        if need_transcode:
            try:
                output_path = transcode_to_wav(input_path)
            except RuntimeError as e:
                error = ValueError(ERROR_MESSAGES[ErrorCode.TRANSCODE_FAILED])
                error.error_code = ErrorCode.TRANSCODE_FAILED
                raise error from e
            finally:
                os.unlink(input_path)
            final_path = output_path
            audio_info = {
                'filename': filename,
                'size': file_size,
                'duration': duration,
                'sample_rate': TARGET_SAMPLE_RATE,
                'channels': TARGET_CHANNELS,
                'sample_width': TARGET_SAMPLE_WIDTH,
                'format': 'wav',
                'transcoded': True
            }
        else:
            final_path = input_path
            audio_info = {
                'filename': filename,
                'size': file_size,
                'duration': duration,
                'sample_rate': sample_rate,
                'channels': channels,
                'sample_width': sample_width,
                'format': file_ext,
                'transcoded': False
            }
        
        return audio_info, final_path
    except Exception:
        if output_path and os.path.exists(output_path):
            try:
                os.unlink(output_path)
            except OSError:
                pass
        if input_path and os.path.exists(input_path):
            try:
                os.unlink(input_path)
            except OSError:
                pass
        raise
