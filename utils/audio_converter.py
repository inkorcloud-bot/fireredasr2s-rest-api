"""
音频转码模块 - 使用 ffmpeg 将各类音频转为 16kHz 16-bit mono PCM WAV
"""

import os
import tempfile
from .logger import get_logger

logger = get_logger(__name__)

# 标准 ASR 输入格式
TARGET_SAMPLE_RATE = 16000
TARGET_CHANNELS = 1
TARGET_SAMPLE_WIDTH = 2  # 16-bit

# FFmpeg 支持解码的音频文件扩展名（硬编码，源自 ffmpeg -formats 输出）
# 包含常见音频格式及 ffmpeg 可识别的扩展名
SUPPORTED_AUDIO_EXTENSIONS = frozenset({
    '3gp', '3g2', '8svx', 'aa', 'aac', 'aax', 'ac3', 'act', 'adp', 'adts',
    'adx', 'aif', 'aiff', 'amr', 'ape', 'asf', 'ast', 'au', 'avr', 'caf',
    'cda', 'dff', 'dsf', 'dsm', 'dss', 'dts', 'eac3', 'ec3', 'f32', 'f64',
    'fap', 'flac', 'flv', 'gsm', 'ircam', 'm2ts', 'm4a', 'm4b', 'm4r',
    'mka', 'mkv', 'mp2', 'mp3', 'mp4', 'mpc', 'mpp', 'mts', 'nut', 'nsv',
    'oga', 'ogg', 'oma', 'opus', 'qcp', 'ra', 'ram', 'rm', 'sln', 'smp',
    'snd', 'sox', 'spx', 'tak', 'tta', 'voc', 'w64', 'wav', 'wave', 'webm',
    'wma', 'wve', 'wv', 'xa', 'xwma',
})


def get_audio_duration_ffprobe(file_path: str) -> float:
    """
    使用 ffprobe 获取任意格式音频的时长（秒）
    """
    try:
        import ffmpeg
        probe = ffmpeg.probe(file_path)
        duration = float(probe['format']['duration'])
        return duration
    except Exception as e:
        logger.error(f"ffprobe 获取时长失败: {e}")
        raise ValueError(f"无法解析音频文件: {e}")


def transcode_to_wav(input_path: str, output_path: str = None) -> str:
    """
    将音频文件转码为 16kHz 16-bit mono PCM WAV
    
    Args:
        input_path: 输入文件路径
        output_path: 输出文件路径，若为 None 则创建临时文件
        
    Returns:
        输出 WAV 文件路径
    """
    import ffmpeg
    
    if output_path is None:
        fd, output_path = tempfile.mkstemp(suffix='.wav')
        os.close(fd)
    
    try:
        stream = ffmpeg.input(input_path)
        stream = ffmpeg.output(
            stream,
            output_path,
            acodec='pcm_s16le',
            ac=TARGET_CHANNELS,
            ar=TARGET_SAMPLE_RATE
        )
        ffmpeg.run(stream, overwrite_output=True, quiet=True)
        logger.info(f"音频转码完成: {input_path} -> {output_path}")
        return output_path
    except ffmpeg.Error as e:
        stderr = e.stderr.decode() if e.stderr else str(e)
        logger.error(f"ffmpeg 转码失败: {stderr}")
        if output_path and os.path.exists(output_path):
            try:
                os.unlink(output_path)
            except OSError:
                pass
        raise RuntimeError(f"音频转码失败: {stderr}")
