"""
Punc 处理器 - 标点预测
"""

import uuid
from typing import List, Dict, Any
from utils.logger import get_logger

logger = get_logger(__name__)


class PuncProcessor:
    """标点预测处理器"""
    
    def __init__(self, model_manager):
        """初始化 Punc 处理器"""
        self.model_manager = model_manager
        self.logger = logger
        
    async def predict(
        self,
        texts: List[str],
        uttids: List[str] = None
    ) -> Dict[str, Any]:
        """
        标点预测
        Returns: {'results': [{'punc_text': str, 'origin_text': str, 'uttid': str}, ...]}
        """
        if not texts:
            return {'results': []}
        
        # 生成默认 uttid
        if uttids is None:
            uttids = [str(uuid.uuid4()) for _ in texts]
        
        if len(texts) != len(uttids):
            raise ValueError("texts 和 uttids 长度不一致")
        
        try:
            # 调用 Punc 模型
            punc_model = self.model_manager.get_model('punc')
            if not punc_model:
                raise RuntimeError("Punc 模型未加载")
            
            results = punc_model.predict(texts, uttids)
            
            return {'results': results}
        except Exception as e:
            self.logger.error(f"Punc 预测失败: {e}")
            raise
