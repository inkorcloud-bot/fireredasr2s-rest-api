"""
日志工具模块
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional

# 存储已配置的 logger 实例
_loggers = {}


def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: str = "INFO",
    max_file_size: int = 10485760,
    backup_count: int = 5
) -> logging.Logger:
    """设置并返回 logger 实例"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # 清除已有的 handlers
    logger.handlers.clear()

    # 日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 控制台日志
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件日志（可选）
    if log_file:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    _loggers[name] = logger
    return logger


def get_logger(name: str) -> logging.Logger:
    """获取已配置的 logger 实例"""
    if name in _loggers:
        return _loggers[name]
    # 如果未配置，返回默认配置的 logger
    return setup_logger(name)
