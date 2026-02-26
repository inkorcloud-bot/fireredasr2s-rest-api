"""
LID 处理器 - 语种识别
"""

import os, tempfile, uuid
from fastapi import UploadFile
from typing import Dict, Any
from ..utils.logger import get_logger
from ..utils.audio_validator import validate_audio_file

logger = get_logger(__name__)


class LIDProcessor:
    """语种识别处理器"""
    
    def __init__(self, model_manager, config: dict):
        self.model_manager = model_manager
        self.config = config
        self.logger = logger
        
    async def detect(self, audio_file: UploadFile) -> Dict[str, Any]:
        uttid = str(uuid.uuid4())
        tmp_path = None
        
        try:
            validate_audio_file(audio_file, self.config)
            content = await audio_file.read()
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
                tmp.write(content)
                tmp_path = tmp.name
            
            lid_model = self.model_manager.get_model('lid')
            if not lid_model:
                raise RuntimeError("LID 模型未加载")
            
            result = lid_model.detect(tmp_path)
            return {
                'uttid': uttid,
                'lang': result['lang'],
                'confidence': result['confidence'],
                'dur_s': result['duration']
            }
        except Exception as e:
            self.logger.error(f"LID 检测失败: {e}")
            raise
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)
