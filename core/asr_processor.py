"""ASR 批量转录处理器"""

import os
import tempfile
import time
from fastapi import UploadFile
from typing import List, Dict, Any
from utils.logger import get_logger
from utils.audio_validator import validate_audio_file
from utils.response_builder import error_response

logger = get_logger(__name__)


class ASRProcessor:
    def __init__(self, model_manager, config: dict):
        self.model_manager = model_manager
        self.config = config
        logger.info("ASRProcessor 初始化完成")

    async def batch_transcribe(
        self,
        audio_files: List[UploadFile],
        uttids: List[str] = None,
        asr_type: str = "aed",
        beam_size: int = 3,
        return_timestamp: bool = False
    ) -> Dict[str, Any]:
        """批量语音识别"""
        results = []
        total_start = time.time()
        asr_model = self.model_manager.get_model('asr')
        
        if not asr_model:
            return error_response(500, "ASR 模型未加载")
        
        for idx, file in enumerate(audio_files):
            try:
                audio_info = validate_audio_file(file, self.config)
                await file.seek(0)
                content = await file.read()
                
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
                    tmp.write(content)
                    tmp_path = tmp.name
                
                try:
                    start = time.time()
                    result = asr_model.transcribe(
                        tmp_path, asr_type=asr_type,
                        beam_size=beam_size,
                        return_timestamp=return_timestamp
                    )
                    results.append({
                        'uttid': uttids[idx] if uttids else f'utt_{idx}',
                        'text': result.get('text', ''),
                        'processing_time_ms': int((time.time() - start) * 1000),
                        'audio_info': audio_info
                    })
                finally:
                    os.unlink(tmp_path)
            except Exception as e:
                logger.error(f"转录失败 {file.filename}: {e}")
                results.append({'error': str(e), 'uttid': uttids[idx] if uttids else f'utt_{idx}'})
        
        return {
            'results': results,
            'total_processing_time_ms': int((time.time() - total_start) * 1000)
        }
