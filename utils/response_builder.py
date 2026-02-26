"""统一响应构造器"""

from typing import Any, Optional
from .error_codes import ErrorCode, ERROR_MESSAGES


def success_response(data: Any = None, message: str = "success") -> dict:
    """构造成功响应"""
    return {
        "code": ErrorCode.SUCCESS,
        "message": message,
        "data": data,
    }


def error_response(code: int, details: Optional[Any] = None) -> dict:
    """构造错误响应"""
    return {
        "code": code,
        "message": ERROR_MESSAGES.get(code, "未知错误"),
        "details": details,
    }
