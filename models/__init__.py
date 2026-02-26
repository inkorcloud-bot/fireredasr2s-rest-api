"""
模型模块 - 导出所有模型类
"""

# 模型类将在各个模块实现后导入
# ASRModel 将从 asr_model.py 导入
# VADModel 将从 vad_model.py 导出
# LIDModel 将从 lid_model.py 导出
# PuncModel 将从 punc_model.py 导出

try:
    from .asr_model import ASRModel
except ImportError:
    ASRModel = None

try:
    from .vad_model import VADModel
except ImportError:
    VADModel = None

try:
    from .lid_model import LIDModel
except ImportError:
    LIDModel = None

try:
    from .punc_model import PuncModel
except ImportError:
    PuncModel = None

__all__ = ['ASRModel', 'VADModel', 'LIDModel', 'PuncModel']
