"""
VAD 模型封装类
"""

import time
from typing import Dict, Any, List
from ..utils.logger import get_logger

logger = get_logger(__name__)


class VADModel:
    """VAD 模型封装类"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化 VAD 模型"""
        self.config = config
        self.model_dir = config.get('model_dir', '')
        self.use_gpu = config.get('use_gpu', False)
        self.speech_threshold = config.get('speech_threshold', 0.5)
        self._loaded = False
        logger.info(f"VAD模型初始化: threshold={self.speech_threshold}")
    
    def load(self) -> None:
        """加载模型"""
        if self._loaded:
            logger.warning("VAD模型已加载，跳过")
            return
        logger.info("正在加载VAD模型...")
        time.sleep(0.3)  # 模拟加载延迟
        self._loaded = True
        logger.info("VAD模型加载完成")
    
    def detect(self, audio_path: str, **kwargs) -> Dict[str, Any]:
        """VAD 检测"""
        if not self._loaded:
            raise RuntimeError("VAD模型未加载")
        
        logger.info(f"VAD检测: {audio_path}")
        time.sleep(0.4)  # 模拟检测延迟
        
        # 模拟返回结果
        return {
            'duration': 4.2,
            'timestamps': [[0.0, 1.5], [2.0, 4.0]]
        }
    
    def aed_detect(self, audio_path: str) -> Dict[str, Any]:
        """音频事件检测"""
        if not self._loaded:
            raise RuntimeError("VAD模型未加载")
        
        logger.info(f"AED检测: {audio_path}")
        time.sleep(0.5)  # 模拟检测延迟
        
        # 模拟返回结果
        return {
            'duration': 4.2,
            'event2timestamps': {'speech': [[0.0, 1.5], [2.0, 4.0]], 'music': []},
            'event2ratio': {'speech': 0.95, 'music': 0.0}
        }
    
    def unload(self) -> None:
        """卸载模型"""
        if not self._loaded:
            logger.warning("VAD模型未加载")
            return
        logger.info("正在卸载VAD模型...")
        self._loaded = False
        logger.info("VAD模型已卸载")
