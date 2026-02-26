"""
模型管理器 - 统一管理所有模型的生命周期
"""

from typing import Dict, Any, Optional
from ..utils.logger import get_logger
from ..utils.config_loader import get_config

logger = get_logger(__name__)


class ModelManager:
    """统一的模型管理器，管理所有模型的生命周期"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化模型管理器，创建所有模型实例但不加载"""
        self.config = config or get_config().get('models', {})
        self._models: Dict[str, Any] = {'asr': None, 'vad': None, 'lid': None, 'punc': None}
        self._loaded: Dict[str, bool] = {'asr': False, 'vad': False, 'lid': False, 'punc': False}
        self._model_classes: Dict[str, Any] = {}
        try:
            from ..models import ASRModel, VADModel, LIDModel, PuncModel
            self._model_classes = {'asr': ASRModel, 'vad': VADModel, 'lid': LIDModel, 'punc': PuncModel}
            logger.info("模型类导入成功")
        except ImportError as e:
            logger.error(f"模型类导入失败: {e}")
    
    def preload_models(self) -> None:
        """根据配置预加载模型，如果 preload_on_start=True 则加载所有启用的模型"""
        if not self.config.get('preload_on_start', False):
            return
        logger.info("开始预加载模型...")
        for name in ['asr', 'vad', 'lid', 'punc']:
            if self.config.get(name, {}).get('enabled', False):
                model_class = self._model_classes.get(name)
                if model_class and not self._loaded[name]:
                    try:
                        self._models[name] = model_class(self.config.get(name, {}))
                        self._loaded[name] = True
                        logger.info(f"{name} 模型加载成功")
                    except Exception as e:
                        logger.error(f"{name} 模型加载失败: {e}")
        logger.info("模型预加载完成")
    
    def reload_modules(self, modules: list) -> Dict[str, list]:
        """热重载指定模块"""
        result = {'success': [], 'failed': []}
        for name in modules:
            if name not in self._models:
                result['failed'].append(name)
                logger.warning(f"未知的模块: {name}")
                continue
            self._models[name] = None
            self._loaded[name] = False
            model_class = self._model_classes.get(name)
            if model_class and not self._loaded[name]:
                try:
                    self._models[name] = model_class(self.config.get(name, {}))
                    self._loaded[name] = True
                    result['success'].append(name)
                    logger.info(f"{name} 模型热重载成功")
                except Exception as e:
                    result['failed'].append(name)
                    logger.error(f"{name} 模型热重载失败: {e}")
            else:
                result['failed'].append(name)
        return result
    
    def get_model(self, module_name: str) -> Optional[Any]:
        """获取指定模型实例，如果未加载则返回 None"""
        return self._models.get(module_name)
    
    def get_status(self) -> Dict[str, str]:
        """获取所有模型加载状态"""
        return {name: 'loaded' if self._loaded[name] else 'unloaded' for name in ['asr', 'vad', 'lid', 'punc']}
