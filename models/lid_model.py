"""
LID 模型封装 - 语种识别
"""

import time
from utils.logger import get_logger


class LIDModel:
    """语种识别模型封装类"""
    
    def __init__(self, config: dict):
        """初始化 LID 模型"""
        self.config = config
        self.logger = get_logger("LIDModel")
        self.model_dir = config.get("model_dir", "")
        self.use_gpu = config.get("use_gpu", False)
        self.use_half = config.get("use_half", False)
        self._loaded = False
        
    def load(self) -> None:
        """加载模型"""
        if self._loaded:
            self.logger.info("模型已加载，跳过")
            return
        self.logger.info(f"加载 LID 模型: {self.model_dir}, GPU: {self.use_gpu}")
        time.sleep(0.1)  # 模拟加载延迟
        self._loaded = True
        self.logger.info("LID 模型加载完成")
        
    def detect(self, audio_path: str) -> dict:
        """
        语种识别
        Returns: {
            'lang': str,
            'confidence': float,
            'duration': float
        }
        """
        if not self._loaded:
            raise RuntimeError("模型未加载，请先调用 load()")
        
        self.logger.info(f"检测音频: {audio_path}")
        time.sleep(0.05)  # 模拟推理延迟
        
        # 模拟返回结果
        return {
            'lang': 'zh-CN',
            'confidence': 0.95,
            'duration': 3.5
        }
        
    def unload(self) -> None:
        """卸载模型"""
        if not self._loaded:
            return
        self.logger.info("卸载 LID 模型")
        self._loaded = False
