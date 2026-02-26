"""
请求处理器 - 一站式语音识别请求处理器
"""

import os
import tempfile
import time
import uuid
from fastapi import UploadFile
from typing import Dict, Any
from ..utils.logger import get_logger
from ..utils.audio_validator import validate_audio_file, get_audio_duration
from ..utils.response_builder import success_response, error_response
from ..utils.error_codes import ErrorCode

logger = get_logger(__name__)


class RequestProcessor:
    """一站式语音识别请求处理器"""
    
    def __init__(self, model_manager, config: dict):
        """初始化请求处理器"""
        self.model_manager = model_manager
        self.config = config
    
    async def transcribe(
        self,
        audio_file: UploadFile,
        uttid: str = None,
        enable_vad: bool = True,
        enable_lid: bool = True,
        enable_punc: bool = True,
        asr_type: str = "aed",
        return_timestamp: bool = False
    ) -> Dict[str, Any]:
        """
        一站式语音识别
        Returns: {
            'uttid': str, 'text': str, 'dur_s': float,
            'sentences': [...], 'vad_segments_ms': [...],
            'words': [...], 'processing_time_ms': int
        }
        """
        start_time = time.time()
        uttid = uttid or str(uuid.uuid4())
        result = {'uttid': uttid, 'text': '', 'dur_s': 0, 'processing_time_ms': 0}
        tmp_path = None
        
        try:
            # 验证音频文件
            audio_info = validate_audio_file(audio_file, self.config)
            result['dur_s'] = audio_info['duration']
            logger.info(f"音频验证成功: {audio_info['filename']}, 时长: {audio_info['duration']:.2f}s")
            
            # 保存临时文件
            audio_file.file.seek(0)
            content = audio_file.file.read()
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
                tmp.write(content)
                tmp_path = tmp.name
            
            # ASR 识别
            asr_model = self.model_manager.get_model('asr')
            if not asr_model:
                raise ValueError("ASR 模型未加载")
            
            asr_result = await asr_model.transcribe(tmp_path, return_timestamp=return_timestamp)
            result['text'] = asr_result.get('text', '')
            result['sentences'] = asr_result.get('sentences', [])
            if return_timestamp:
                result['words'] = asr_result.get('words', [])
            
            # VAD 检测
            if enable_vad:
                vad_model = self.model_manager.get_model('vad')
                if vad_model:
                    vad_result = await vad_model.detect(tmp_path)
                    result['vad_segments_ms'] = vad_result.get('segments', [])
            
            # LID 检测
            if enable_lid:
                lid_model = self.model_manager.get_model('lid')
                if lid_model:
                    lid_result = await lid_model.detect(tmp_path)
                    result['language'] = lid_result.get('language', 'unknown')
                    result['language_score'] = lid_result.get('score', 0)
            
            # Punc 预测
            if enable_punc and result['text']:
                punc_model = self.model_manager.get_model('punc')
                if punc_model:
                    punc_result = await punc_model.predict(result['text'])
                    result['text'] = punc_result.get('text', result['text'])
            
        except Exception as e:
            logger.error(f"语音识别失败: {e}")
            raise
        finally:
            # 清理临时文件
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)
        
        result['processing_time_ms'] = int((time.time() - start_time) * 1000)
        logger.info(f"识别完成: uttid={uttid}, 耗时={result['processing_time_ms']}ms")
        return result
