"""
错误码定义模块
"""


class ErrorCode:
    """错误码常量定义"""
    SUCCESS = 0
    INVALID_PARAMS = 4000
    INVALID_AUDIO_FORMAT = 4001
    AUDIO_FILE_TOO_LARGE = 4002
    AUDIO_DURATION_EXCEEDED = 4003
    MODEL_NOT_LOADED = 4010
    TRANSCODE_FAILED = 4004
    JOB_NOT_FOUND = 4005
    INTERNAL_SERVER_ERROR = 5000
    MODEL_INFERENCE_ERROR = 5001
    GPU_OUT_OF_MEMORY = 5002


# 错误码到错误信息的映射
ERROR_MESSAGES = {
    ErrorCode.SUCCESS: "成功",
    ErrorCode.INVALID_PARAMS: "无效的请求参数",
    ErrorCode.INVALID_AUDIO_FORMAT: "不支持的音频格式",
    ErrorCode.AUDIO_FILE_TOO_LARGE: "音频文件过大",
    ErrorCode.AUDIO_DURATION_EXCEEDED: "音频时长超过限制",
    ErrorCode.TRANSCODE_FAILED: "音频转码失败",
    ErrorCode.JOB_NOT_FOUND: "任务不存在或已过期",
    ErrorCode.MODEL_NOT_LOADED: "模型未加载",
    ErrorCode.INTERNAL_SERVER_ERROR: "内部服务器错误",
    ErrorCode.MODEL_INFERENCE_ERROR: "模型推理错误",
    ErrorCode.GPU_OUT_OF_MEMORY: "GPU内存不足",
}
