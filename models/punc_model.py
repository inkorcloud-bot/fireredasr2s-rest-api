"""
Punc 模型封装 - 标点预测预测
"""

import time
from utils.logger import get_logger

# 导入 FireRedPunc 相关模块
try:
    from fireredasr2s.fireredpunc import FireRedPunc, FireRedPuncConfig
    FIRERED_AVAILABLE = True
except ImportError:
    FIRERED_AVAILABLE = False


class PuncModel:
    """标点预测模型封装类"""
    
    def __init__(self, config: dict):
        """初始化 Punc 模型"""
        self.config = config
        self.logger = get_logger("PuncModel")
        self.model_dir = config.get("model_dir", "")
        self.use_gpu = config.get("use_gpu", False)
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
        
        self.logger.info(f"加载 Punc 模型: {self.model_dir}, GPU: {self.use_gpu}")
        
        # 创建 Punc 配置
        punc_config = FireRedPuncConfig(
            use_gpu=self.use_gpu
        )
        
        # 加载模型
        self._model = FireRedPunc.from_pretrained(self.model_dir, punc_config)
        
        self._loaded = True
        self.logger.info("Punc 模型加载完成")
        
    def predict(self, texts: list, uttids: list = None) -> list:
        """
        标点预测
        Returns: [
            {
                'punc_text': str,
                'origin_text': str,
                'uttid': str
            },
            ...
        ]
        """
        if not self._loaded:
            raise RuntimeError("模型未加载，请先调用 load()")
        
        if uttids is None:
            uttids = [f"txt_{i}" for i in range(len(texts))]
            
        if len(texts) != len(uttids):
            raise ValueError("texts 和 uttids 长度不一致")
            
        self.logger.info(f"预测标点，数量: {len(texts)}")
        
        results = self._model.process(texts, uttids)
        
        # 转换为统一格式
        return [
            {
                'punc_text': r.get('punc_text', ''),
                'origin_text': r.get('origin_text', ''),
                'uttid': r.get('uttid', '')
            }
            for r in results
        ]
        
    def unload(self) -> None:
        """卸载模型"""
        if not self._loaded:
            return
        self.logger.info("卸载 Punc 模型")
        self._loaded = False
