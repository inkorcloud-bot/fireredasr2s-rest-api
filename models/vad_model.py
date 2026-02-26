"""
VAD 模型封装类
"""

import time
from typing import Dict, Any, List
from utils.logger import get_logger

# 导入 FireRedVAD 和 FireRedAed 相关模块
try:
    from fireredasr2s.fireredvad import FireRedVad, FireRedVadConfig
    from fireredasr2s.fireredvad import FireRedAed, FireRedAedConfig
    FIRERED_AVAILABLE = True
except ImportError:
    FIRERED_AVAILABLE = False

logger = get_logger(__name__)


class VADModel:
    """VAD 模型封装类"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化 VAD 模型"""
        self.config = config
        self.model_dir = config.get('model_dir', '')
        self.stream_model_dir = config.get('stream_model_dir', '')
        self.aed_model_dir = config.get('aed_model_dir', '')
        self.use_gpu = config.get('use_gpu', False)
        self.speech_threshold = config.get('speech_threshold', 0.5)
        self._loaded = False
        self._vad_model = None
        self._aed_model = None
        logger.info(f"VAD模型初始化: threshold={self.speech_threshold}")
    
    def load(self) -> None:
        """加载模型"""
        if self._loaded:
            logger.warning("VAD模型已加载，跳过")
            return
        
        if not FIRERED_AVAILABLE:
            logger.error("FireRedASR2S 库不可用，无法加载真实模型")
            raise RuntimeError("FireRedASR2S 库不可用")
        
        logger.info("正在加载VAD模型...")
        
        # 创建 VAD 配置
        vad_config = FireRedVadConfig(
            use_gpu=self.use_gpu,
            threshold=self.speech_threshold
        )
        
        # 创建 AED 配置
        aed_config = FireRedAedConfig(
            use_gpu=self.use_gpu
        )
        
        # 加载 VAD 模型
        self._vad_model = FireRedVad.from_pretrained(self.model_dir, vad_config)
        
        # 加载 AED 模型
        self._aed_model = FireRedAed.from_pretrained(self.aed_model_dir, aed_config)
        
        self._loaded = True
        logger.info("VAD模型加载完成")
    
    def detect(self, audio_path: str, **kwargs) -> Dict[str, Any]:
        """VAD 检测"""
        if not self._loaded:
            raise RuntimeError("VAD模型未加载")
        
        logger.info(f"VAD检测: {audio_path}")
        
        result, _ = self._vad_model.detect(audio_path)
        
        return {
            'dur': result.get('dur', 0.0),
            'timestamps': result.get('timestamps', [])
        }
    
    def aed_detect(self, audio_path: str) -> Dict[str, Any]:
        """音频事件检测"""
        if not self._loaded:
            raise RuntimeError("VAD模型未加载")
        
        logger.info(f"AED检测: {audio_path}")
        
        result, _ = self._aed_model.detect(audio_path)
        
        return {
            'dur': result.get('dur', 0.0),
            'event2timestamps': result.get('event2timestamps', {}),
            'event2ratio': result.get('event2ratio', {})
        }
    
    def unload(self) -> None:
        """卸载模型"""
        if not self._loaded:
            logger.warning("VAD模型未加载")
            return
        logger.info("正在卸载VAD模型...")
        self._loaded = False
        logger.info("VAD模型已卸载")
