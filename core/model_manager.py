"""
模型管理器 - 统一管理所有模型的生命周期
以 FireRedAsr2System 为单一模型源，独立模块从 FireRedAsr2System 中提取
"""

from typing import Dict, Any, Optional, Callable

from utils.logger import get_logger
from utils.config_loader import get_config

logger = get_logger(__name__)


class ModelManager:
    """统一的模型管理器，从 FireRedAsr2System 提取各模块"""

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        asr_system: Optional[Any] = None,
        on_reload: Optional[Callable[[Any], None]] = None
    ):
        self.config = config or get_config().get('models', {})
        self._asr_system = asr_system
        self._on_reload = on_reload

    def set_asr_system(self, asr_system: Optional[Any]) -> None:
        """设置或更新 asr_system 引用"""
        self._asr_system = asr_system

    async def initialize(self) -> None:
        """异步初始化（保持接口兼容，统一模式下无需预加载）"""
        pass

    async def cleanup(self) -> None:
        """异步清理：释放模型资源"""
        self._asr_system = None
        logger.info("模型资源已释放")

    def preload_models(self) -> None:
        """统一模式下由 FireRedAsr2System 负责加载，此处为 no-op"""
        pass

    def reload_modules(self, modules: Optional[list] = None) -> Dict[str, list]:
        """热重载：重建整个 FireRedAsr2System"""
        from core.asr_system_factory import create_asr_system

        result = {'success': [], 'failed': []}
        try:
            new_system = create_asr_system(self.config)
            if self._on_reload:
                self._on_reload(new_system)
            self._asr_system = new_system
            for name in (modules or ['asr', 'vad', 'lid', 'punc']):
                if name in ['asr', 'vad', 'lid', 'punc']:
                    result['success'].append(name)
            logger.info("FireRedAsr2System 热重载成功")
        except Exception as e:
            logger.error(f"FireRedAsr2System 热重载失败: {e}")
            result['failed'] = modules or ['asr', 'vad', 'lid', 'punc']
        return result

    def get_model(self, module_name: str) -> Optional[Any]:
        """获取指定模块的适配器实例，若 asr_system 无对应子模块则返回 None"""
        from core.adapters import ASRAdapter, VADAdapter, LIDAdapter, PuncAdapter

        if not self._asr_system:
            return None

        if module_name == 'asr' and self._asr_system.asr is not None:
            return ASRAdapter(self._asr_system.asr)
        if module_name == 'vad' and self._asr_system.vad is not None:
            return VADAdapter(self._asr_system.vad)
        if module_name == 'lid' and self._asr_system.lid is not None:
            return LIDAdapter(self._asr_system.lid)
        if module_name == 'punc' and self._asr_system.punc is not None:
            return PuncAdapter(self._asr_system.punc)
        return None

    def get_status(self) -> Dict[str, str]:
        """获取所有模型加载状态（基于 asr_system）"""
        if not self._asr_system:
            return {'asr': 'unloaded', 'vad': 'unloaded', 'lid': 'unloaded', 'punc': 'unloaded'}

        c = self._asr_system.config
        return {
            'asr': 'loaded' if self._asr_system.asr is not None else 'unloaded',
            'vad': 'loaded' if (c.enable_vad and self._asr_system.vad is not None) else 'unloaded',
            'lid': 'loaded' if (c.enable_lid and self._asr_system.lid is not None) else 'unloaded',
            'punc': 'loaded' if (c.enable_punc and self._asr_system.punc is not None) else 'unloaded',
        }
