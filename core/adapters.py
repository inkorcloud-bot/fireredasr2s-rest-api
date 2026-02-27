"""
适配器层 - 将 FireRedAsr2System 内部模型封装为与 ASRModel/VADModel/LIDModel/PuncModel 相同的接口
"""

from typing import Dict, Any, List, Optional

from utils.logger import get_logger

logger = get_logger(__name__)


class ASRAdapter:
    """封装 FireRedAsr2.asr，暴露 transcribe 接口"""

    def __init__(self, asr_model: Any):
        self._model = asr_model

    def transcribe(self, audio_path: str, **kwargs) -> Dict[str, Any]:
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


class VADAdapter:
    """封装 FireRedAsr2System.vad，暴露 detect 接口。不含 aed_detect（FireRedAsr2System 无 FireRedAed）"""

    def __init__(self, vad_model: Any):
        self._model = vad_model

    def detect(self, audio_path: str, **kwargs) -> Dict[str, Any]:
        result, _ = self._model.detect(audio_path)
        return {
            'dur': result.get('dur', 0.0),
            'timestamps': result.get('timestamps', [])
        }

    def supports_aed(self) -> bool:
        """FireRedAsr2System 不包含 FireRedAed"""
        return False


class LIDAdapter:
    """封装 FireRedAsr2System.lid，暴露 detect 接口"""

    def __init__(self, lid_model: Any):
        self._model = lid_model

    def detect(self, audio_path: str) -> Dict[str, Any]:
        uttid = 'tmp'
        batch_uttid = [uttid]
        batch_wav_path = [audio_path]
        results = self._model.process(batch_uttid, batch_wav_path)
        result = results[0]
        return {
            'lang': result.get('lang', ''),
            'confidence': result.get('confidence', 0.0),
            'duration': result.get('dur_s', 0.0)
        }


class PuncAdapter:
    """封装 FireRedAsr2System.punc，暴露 predict 接口"""

    def __init__(self, punc_model: Any):
        self._model = punc_model

    def predict(self, texts: List[str], uttids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        if uttids is None:
            uttids = [f"txt_{i}" for i in range(len(texts))]
        if len(texts) != len(uttids):
            raise ValueError("texts 和 uttids 长度不一致")
        results = self._model.process(texts, uttids)
        return [
            {
                'punc_text': r.get('punc_text', ''),
                'origin_text': r.get('origin_text', ''),
                'uttid': r.get('uttid', '')
            }
            for r in results
        ]
