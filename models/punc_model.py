"""
Punc 模型封装 - 标点预测
"""

import time
from utils.logger import get_logger


class PuncModel:
    """标点预测模型封装类"""
    
    def __init__(self, config: dict):
        """初始化 Punc 模型"""
        self.config = config
        self.logger = get_logger("PuncModel")
        self.model_dir = config.get("model_dir", "")
        self.use_gpu = config.get("use_gpu", False)
        self._loaded = False
        
    def load(self) -> None:
        """加载模型"""
        if self._loaded:
            self.logger.info("模型已加载，跳过")
            return
        self.logger.info(f"加载 Punc 模型: {self.model_dir}, GPU: {self.use_gpu}")
        time.sleep(0.1)  # 模拟加载延迟
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
            uttids = [f"utt_{i}" for i in range(len(texts))]
            
        if len(texts) != len(uttids):
            raise ValueError("texts 和 uttids 长度不一致")
            
        self.logger.info(f"预测标点，数量: {len(texts)}")
        time.sleep(0.02 * len(texts))  # 模拟推理延迟
        
        results = []
        for i, text in enumerate(texts):
            # 模拟添加标点
            punc_text = text + "。"
            results.append({
                'punc_text': punc_text,
                'origin_text': text,
                'uttid': uttids[i]
            })
        
        return results
        
    def unload(self) -> None:
        """卸载模型"""
        if not self._loaded:
            return
        self.logger.info("卸载 Punc 模型")
        self._loaded = False
