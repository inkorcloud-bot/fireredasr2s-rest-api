"""
ASR System 工厂模块
从 config.yaml 的 models 配置构建 FireRedAsr2System
不改动 FireRedASR2S 源码
"""

from typing import Dict, Any

from utils.logger import get_logger

logger = get_logger(__name__)


def summarize_models_config(models_config: Dict[str, Any]) -> Dict[str, Any]:
    """提取便于排查的模型配置摘要，避免日志过长。"""
    asr_cfg = models_config.get("asr") or {}
    vad_cfg = models_config.get("vad") or {}
    lid_cfg = models_config.get("lid") or {}
    punc_cfg = models_config.get("punc") or {}

    return {
        "asr": {
            "enabled": asr_cfg.get("enabled", False),
            "type": asr_cfg.get("type", "aed"),
            "model_dir": asr_cfg.get("model_dir", "pretrained_models/FireRedASR2-AED"),
            "use_gpu": asr_cfg.get("use_gpu", True),
            "use_half": asr_cfg.get("use_half", False),
            "beam_size": asr_cfg.get("beam_size", 5),
        },
        "vad": {
            "enabled": vad_cfg.get("enabled", True),
            "model_dir": vad_cfg.get("model_dir", "pretrained_models/FireRedVAD/VAD"),
            "use_gpu": vad_cfg.get("use_gpu", True),
            "speech_threshold": vad_cfg.get("speech_threshold", 0.5),
        },
        "lid": {
            "enabled": lid_cfg.get("enabled", True),
            "model_dir": lid_cfg.get("model_dir", "pretrained_models/FireRedLID"),
            "use_gpu": lid_cfg.get("use_gpu", True),
            "use_half": lid_cfg.get("use_half", False),
        },
        "punc": {
            "enabled": punc_cfg.get("enabled", True),
            "model_dir": punc_cfg.get("model_dir", "pretrained_models/FireRedPunc"),
            "use_gpu": punc_cfg.get("use_gpu", True),
        },
    }


def summarize_asr_system_config(config: "FireRedAsr2SystemConfig") -> Dict[str, Any]:
    """提取 FireRedAsr2SystemConfig 的关键信息用于日志。"""
    return {
        "asr_type": config.asr_type,
        "asr_model_dir": config.asr_model_dir,
        "vad_model_dir": config.vad_model_dir,
        "lid_model_dir": config.lid_model_dir,
        "punc_model_dir": config.punc_model_dir,
        "enable_vad": config.enable_vad,
        "enable_lid": config.enable_lid,
        "enable_punc": config.enable_punc,
        "asr_use_gpu": config.asr_config.use_gpu,
        "asr_use_half": config.asr_config.use_half,
        "asr_beam_size": config.asr_config.beam_size,
        "vad_use_gpu": config.vad_config.use_gpu,
        "lid_use_gpu": config.lid_config.use_gpu,
        "lid_use_half": config.lid_config.use_half,
        "punc_use_gpu": config.punc_config.use_gpu,
    }


def build_asr_system_config(models_config: Dict[str, Any]) -> "FireRedAsr2SystemConfig":
    """从 config.yaml 的 models 节构建 FireRedAsr2SystemConfig"""
    from fireredasr2s.fireredasr2system import FireRedAsr2SystemConfig
    from fireredasr2s.fireredasr2 import FireRedAsr2Config
    from fireredasr2s.fireredvad import FireRedVadConfig
    from fireredasr2s.fireredlid import FireRedLidConfig
    from fireredasr2s.fireredpunc import FireRedPuncConfig

    def _get(cfg: dict, key: str, default: Any = None) -> Any:
        return cfg.get(key, default) if cfg else default

    asr_cfg = models_config.get("asr") or {}
    vad_cfg = models_config.get("vad") or {}
    lid_cfg = models_config.get("lid") or {}
    punc_cfg = models_config.get("punc") or {}

    vad_config = FireRedVadConfig(
        use_gpu=_get(vad_cfg, "use_gpu", True),
        smooth_window_size=5,
        speech_threshold=_get(vad_cfg, "speech_threshold", 0.5),
        min_speech_frame=20,
        max_speech_frame=2000,
        min_silence_frame=20,
        merge_silence_frame=0,
        extend_speech_frame=0,
        chunk_max_frame=30000,
    )

    lid_config = FireRedLidConfig(
        use_gpu=_get(lid_cfg, "use_gpu", True),
        use_half=_get(lid_cfg, "use_half", False),
    )

    asr_config = FireRedAsr2Config(
        use_gpu=_get(asr_cfg, "use_gpu", True),
        use_half=_get(asr_cfg, "use_half", False),
        beam_size=_get(asr_cfg, "beam_size", 5),
        nbest=1,
        decode_max_len=0,
        softmax_smoothing=1.25,
        aed_length_penalty=0.6,
        eos_penalty=1.0,
        return_timestamp=False,
        decode_min_len=0,
        repetition_penalty=1.0,
        llm_length_penalty=0.0,
        temperature=1.0,
        elm_dir="",
        elm_weight=0.0,
    )

    punc_config = FireRedPuncConfig(
        use_gpu=_get(punc_cfg, "use_gpu", True),
        sentence_max_length=-1,
    )

    asr_system_config = FireRedAsr2SystemConfig(
        vad_model_dir=_get(vad_cfg, "model_dir", "pretrained_models/FireRedVAD/VAD"),
        lid_model_dir=_get(lid_cfg, "model_dir", "pretrained_models/FireRedLID"),
        asr_type=_get(asr_cfg, "type", "aed"),
        asr_model_dir=_get(asr_cfg, "model_dir", "pretrained_models/FireRedASR2-AED"),
        punc_model_dir=_get(punc_cfg, "model_dir", "pretrained_models/FireRedPunc"),
        vad_config=vad_config,
        lid_config=lid_config,
        asr_config=asr_config,
        punc_config=punc_config,
        asr_batch_size=1,
        punc_batch_size=1,
        enable_vad=_get(vad_cfg, "enabled", True),
        enable_lid=_get(lid_cfg, "enabled", True),
        enable_punc=_get(punc_cfg, "enabled", True),
    )

    return asr_system_config


def create_asr_system(models_config: Dict[str, Any]) -> "FireRedAsr2System":
    """从 config 创建 FireRedAsr2System 实例"""
    from fireredasr2s.fireredasr2system import FireRedAsr2System

    logger.info("收到模型配置，开始构建 FireRedAsr2System: %s", summarize_models_config(models_config))
    config = build_asr_system_config(models_config)
    logger.info("正在创建 FireRedAsr2System，构建后的配置摘要: %s", summarize_asr_system_config(config))
    system = FireRedAsr2System(config)
    logger.info("FireRedAsr2System 创建完成")
    return system
