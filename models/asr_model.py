"""
ASR 模型封装类
"""

import time
from typing import Dict, Any
from ..utils.logger import get_logger

# 导入 FireRedASR2S 相关模块
try:
    from fireredasr2s.fireredasr2 import FireRedAsr2, FireRedAsr2Config
    FIRERED_AVAILABLE = True
except ImportError:
    FIRERED_AVAILABLE = False

logger = get_logger(__name__)


class ASRModel:
    """ASR 模型封装类"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化 ASR 模型"""
        self.config = config
        self.model_dir = config.get('model_dir', '')
        self.use_gpu = config.get('use_gpu', False)
        self.use_half = config.get('use_half', False)
        self.beam_size = config.get('beam_size', 5)
        self.asr_type = config.get('type', 'aed')  # 'aed' 或 'llm'
        self._loaded = False
        self._model = None
        logger.info(f"ASR模型初始化: type={self.asr_type}, gpu={self.use_gpu}, half={self.use_half}")
    
    def load(self) -> None:
        """加载模型"""
        if self._loaded:
            logger.warning("ASR模型已加载，跳过")
            return
        
        if not FIRERED_AVAILABLE:
            logger.error("FireRedASR2S 库不可用，无法加载真实模型")
            raise RuntimeError("FireRedASR2S 库不可用")
        
        logger.info("正在加载ASR模型...")
        
        # 创建 ASR 配置
        asr_config = FireRedAsr2Config(
            use_gpu=self.use_gpu,
            use_half=self.use_half,
            beam_size=self.beam_size,
            return_timestamp=True
        )
        
        # 加载模型
        self._model = FireRedAsr2.from_pretrained(
            self.asr_type,
            self.model_dir,
            asr_config
        )
        
        self._loaded = True
        logger.info("ASR模型加载完成")
    
    def transcribe(self, audio_path: str, **kwargs) -> Dict[str, Any]:
        """语音识别"""
        if not self._loaded:
            raise RuntimeError("ASR模型未加载")
        
        logger.info(f"开始识别音频: {audio_path}")
        
        # FireRedASR2 使用批量处理
        uttid = kwargs.get('uttid', 'tmp')
        batch_uttid = [uttid]
        batch_wav_path = [audio_path]
        
        results = self._model.transcribe(batch_uttid, batch_wav_path)
        result = results[0]
        
        return {
            'text': result.get('text', ''),
            'confidence': result.get('confidence', 0.0),
            'duration': result.get('dur_s', 0.0),
            'timestamp': result.get('timestamp', [])
        }
    
    def unload(self) -> None:
        """卸载模型，释放资源"""
        if not self._loaded:
            logger.warning("ASR模型未加载")
            return
        logger.info("正在卸载ASR模型...")
        self._loaded = False
        logger.info("ASR模型已卸载")
