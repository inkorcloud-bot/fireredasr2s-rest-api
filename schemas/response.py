"""响应模型定义"""

from typing import Any, Optional
from pydantic import BaseModel


class BaseResponse(BaseModel):
    """基础响应类"""
    code: int
    message: str


class SuccessResponse(BaseModel):
    """成功响应"""
    code: int = 0
    message: str = "success"
    data: Any = None


class ErrorResponse(BaseModel):
    """错误响应"""
    code: int
    message: str
    details: Optional[Any] = None


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    version: str
    models_loaded: bool


class TranscribeResponseData(BaseModel):
    """识别结果数据"""
    text: str
    language: Optional[str] = None
    duration: float
    segments: Optional[list] = None


class ASRTranscribeResponseData(BaseModel):
    """ASR 批量结果"""
    results: list
    total_duration: float
