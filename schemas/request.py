"""请求模型定义"""

from typing import Optional
from pydantic import BaseModel, Field


class TranscribeRequest(BaseModel):
    """一站式语音识别请求参数"""
    audio_data: bytes = Field(..., description="音频二进制数据")
    audio_format: str = Field(default="wav", description="音频格式")
    language: Optional[str] = Field(default=None, description="语言代码")
    use_vad: bool = Field(default=True, description="是否启用VAD")
    use_punctuation: bool = Field(default=True, description="是否添加标点")


class ASRTranscribeRequest(BaseModel):
    """ASR 批量转录请求参数"""
    audio_data: bytes = Field(..., description="音频二进制数据")
    model_name: str = Field(default="default", description="模型名称")


class VADDetectRequest(BaseModel):
    """VAD 检测请求参数"""
    audio_data: bytes = Field(..., description="音频二进制数据")
    threshold: float = Field(default=0.5, description="检测阈值")
    min_speech_duration_ms: int = Field(default=250, description="最小语音时长(毫秒)")


class LIDDetectRequest(BaseModel):
    """LID 检测请求参数"""
    audio_data: bytes = Field(..., description="音频二进制数据")
    top_k: int = Field(default=5, description="返回前K个结果")


class PuncPredictRequest(BaseModel):
    """标点预测请求参数"""
    text: str = Field(..., description="待加标点的文本")
    language: Optional[str] = Field(default=None, description="语言代码")


class ReloadModelsRequest(BaseModel):
    """模型重载请求参数"""
    model_name: Optional[str] = Field(default=None, description="模型名称，None表示重载所有")
