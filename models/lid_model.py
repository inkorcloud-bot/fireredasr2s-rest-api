"""
LID 模型封装 - 语种识别
"""

import time
from utils.logger import get_logger

# 导入 FireRedLID 相关模块
try:
    from fireredasr2s.fireredlid import FireRedLid, FireRedLidConfig
    FIRERED_AVAILABLE = True
except ImportError:
    FIRERED_AVAILABLE = False


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
        self._model = None
        
    def load(self) -> None:
        """加载模型"""
        if self._loaded:
            self.logger.info("模型已加载，跳过")
            return
        
        if not FIRERED_AVAILABLE:
            self.logger.error("FireRedASR2S 库不可用，无法加载真实模型")
            raise RuntimeError("FireRedASR2S 库不可用")
        
        self.logger.info(f"加载 LID 模型: {self.model_dir}, GPU: {self.use_gpu}")
        
        # 创建 LID 配置
        lid_config = FireRedLidConfig(
            use_gpu=self.use_gpu,
            use_half=self.use_half
        )
        
        # 加载模型
        self._model = FireRedLid.from_pretrained(self.model_dir, lid_config)
        
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
        
        # FireRedLID 使用批量处理
        uttid = 'tmp'
        batch_uttid = [uttid]
        batch_wav_path = [audio_path]
        
        results = self._model.process(batch_uttid, batch_wav_path)
        result = results[0]
        
        return {
            'lang': result.get('lang', ''),
            'confidence': result.get('confidence', 0.0),
            'duration': result.get('dur_s', 0.0)
        }
        
    def unload(self) -> None:
        """卸载模型"""
        if not self._loaded:
            return
        self.logger.info("卸载 LID 模型")
        self._loaded = False
