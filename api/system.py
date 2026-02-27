"""系统一站式识别路由

使用 FireRedAsr2System.process 执行 VAD→ASR→LID→Punc 完整流水线。
enable_vad/enable_lid/enable_punc/asr_type/return_timestamp 由 config.yaml 决定，
请求参数保留以兼容现有调用。

支持两种模式：
- 同步：POST /system/transcribe，等待识别完成后返回
- 异步：POST /system/transcribe/submit 提交任务，轮询 status/result
"""

import asyncio
import tempfile
import os
from fastapi import APIRouter, UploadFile, File, Form, Depends, Request
from typing import Dict, Any, Optional
from core.model_manager import ModelManager
from core.processor import RequestProcessor
from core.job_store import job_store, STATUS_PENDING, STATUS_PROCESSING, STATUS_COMPLETED, STATUS_FAILED
from api.deps import get_model_manager, get_asr_system
from utils.response_builder import success_response, error_response
from utils.error_codes import ErrorCode

router = APIRouter(tags=["system"])


@router.post("/system/transcribe")
async def system_transcribe(
    audio: UploadFile = File(..., description="音频文件"),
    uttid: str = Form(None, description="话语ID"),
    enable_vad: bool = Form(True, description="启用VAD（以 config 为准）"),
    enable_lid: bool = Form(True, description="启用LID（以 config 为准）"),
    enable_punc: bool = Form(True, description="启用标点（以 config 为准）"),
    asr_type: str = Form("aed", description="ASR类型（以 config 为准）"),
    return_timestamp: bool = Form(False, description="返回时间戳（以 config 为准）"),
    manager: Optional[ModelManager] = Depends(get_model_manager),
    asr_system: Optional[Any] = Depends(get_asr_system),
) -> Dict[str, Any]:
    """
    一站式语音识别接口
    调用 FireRedAsr2System.process 执行 ASR、VAD、LID、标点预测的完整流水线
    """
    try:
        if not asr_system:
            return error_response(500, "ASR System 未加载，请检查 config 中 asr.enabled")
        processor = RequestProcessor(manager, {})
        result = await processor.transcribe(
            audio_file=audio,
            asr_system=asr_system,
            uttid=uttid,
            enable_vad=enable_vad,
            enable_lid=enable_lid,
            enable_punc=enable_punc,
            asr_type=asr_type,
            return_timestamp=return_timestamp,
        )
        return success_response(result, "识别成功")
    except Exception as e:
        return error_response(500, str(e))


async def _run_transcribe_job(job_id: str, app: Any) -> None:
    """后台执行转录任务"""
    from utils.logger import get_logger
    logger = get_logger(__name__)
    job = job_store.get_full(job_id)
    if not job or job["status"] != STATUS_PENDING:
        return
    job_store.set_processing(job_id)
    tmp_path = job.get("tmp_path")
    if not tmp_path or not os.path.exists(tmp_path):
        job_store.set_failed(job_id, "临时文件丢失")
        return
    manager = getattr(app.state, "model_manager", None)
    asr_system = getattr(app.state, "asr_system", None)
    if not asr_system:
        job_store.set_failed(job_id, "ASR System 未加载")
        _cleanup_tmp(tmp_path)
        return
    params = job.get("params") or {}
    try:
        processor = RequestProcessor(manager or {}, {})
        result = await processor.transcribe_from_path(
            file_path=tmp_path,
            filename=job.get("filename", "audio.wav"),
            asr_system=asr_system,
            uttid=job.get("uttid"),
            enable_vad=params.get("enable_vad", True),
            enable_lid=params.get("enable_lid", True),
            enable_punc=params.get("enable_punc", True),
            asr_type=params.get("asr_type", "aed"),
            return_timestamp=params.get("return_timestamp", False),
        )
        job_store.set_completed(job_id, result)
        logger.info(f"异步任务完成: job_id={job_id}")
    except Exception as e:
        job_store.set_failed(job_id, str(e))
        logger.error(f"异步任务失败: job_id={job_id}, error={e}")
    finally:
        _cleanup_tmp(tmp_path)


def _cleanup_tmp(path: str) -> None:
    if path and os.path.exists(path):
        try:
            os.unlink(path)
        except OSError:
            pass


@router.post("/system/transcribe/submit")
async def system_transcribe_submit(
    request: Request,
    audio: UploadFile = File(..., description="音频文件"),
    uttid: str = Form(None, description="话语ID"),
    enable_vad: bool = Form(True, description="启用VAD"),
    enable_lid: bool = Form(True, description="启用LID"),
    enable_punc: bool = Form(True, description="启用标点"),
    asr_type: str = Form("aed", description="ASR类型"),
    return_timestamp: bool = Form(False, description="返回时间戳"),
    manager: Optional[ModelManager] = Depends(get_model_manager),
    asr_system: Optional[Any] = Depends(get_asr_system),
) -> Dict[str, Any]:
    """
    提交异步转录任务（适用于长时间音频）
    立即返回 job_id，客户端轮询 /status/{job_id} 和 /result/{job_id} 获取进度和结果
    """
    try:
        if not asr_system:
            return error_response(500, "ASR System 未加载，请检查 config 中 asr.enabled")
        content = await audio.read()
        filename = audio.filename or "audio.wav"
        suffix = os.path.splitext(filename)[1] or ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        job_id = job_store.create(
            tmp_path=tmp_path,
            filename=filename,
            uttid=uttid,
            params={
                "enable_vad": enable_vad,
                "enable_lid": enable_lid,
                "enable_punc": enable_punc,
                "asr_type": asr_type,
                "return_timestamp": return_timestamp,
            },
        )
        asyncio.create_task(_run_transcribe_job(job_id, request.app))
        return success_response({"job_id": job_id}, "任务已提交，请轮询 /status/{job_id} 获取进度")
    except Exception as e:
        return error_response(500, str(e))


@router.get("/system/transcribe/status/{job_id}")
async def system_transcribe_status(job_id: str) -> Dict[str, Any]:
    """查询转录任务状态"""
    job = job_store.get(job_id)
    if not job:
        return error_response(ErrorCode.JOB_NOT_FOUND, f"任务 {job_id} 不存在或已过期")
    return success_response({
        "job_id": job_id,
        "status": job["status"],
        "filename": job.get("filename"),
        "created_at": job.get("created_at"),
    })


@router.get("/system/transcribe/result/{job_id}")
async def system_transcribe_result(job_id: str) -> Dict[str, Any]:
    """获取转录结果（仅当 status=completed 时返回结果，status=failed 时返回错误信息）"""
    job = job_store.get(job_id)
    if not job:
        return error_response(ErrorCode.JOB_NOT_FOUND, f"任务 {job_id} 不存在或已过期")
    status = job["status"]
    if status == STATUS_COMPLETED:
        return success_response(job["result"], "识别成功")
    if status == STATUS_FAILED:
        return error_response(500, job.get("error", "识别失败"))
    return success_response(
        {"status": status, "message": "任务尚未完成，请稍后重试"},
        "任务进行中",
    )
