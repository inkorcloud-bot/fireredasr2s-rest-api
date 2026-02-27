"""
异步转录任务存储
内存存储，用于 submit/status/result 轮询模式
"""

import time
import uuid
from typing import Dict, Any, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

# 任务状态
STATUS_PENDING = "pending"
STATUS_PROCESSING = "processing"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"

# 最大保留任务数，超出时清理最老的已完成/失败任务
MAX_JOBS = 1000


class JobStore:
    """异步转录任务存储（进程内内存）"""

    def __init__(self):
        self._jobs: Dict[str, Dict[str, Any]] = {}
        self._order: list = []  # 用于 LRU 清理

    def create(
        self,
        tmp_path: str,
        filename: str,
        uttid: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> str:
        """创建任务，返回 job_id"""
        job_id = str(uuid.uuid4())
        self._jobs[job_id] = {
            "status": STATUS_PENDING,
            "created_at": time.time(),
            "tmp_path": tmp_path,
            "filename": filename,
            "uttid": uttid,
            "params": params or {},
            "result": None,
            "error": None,
        }
        self._order.append(job_id)
        self._maybe_cleanup()
        return job_id

    def get(self, job_id: str) -> Optional[Dict[str, Any]]:
        """获取任务信息（不含敏感字段）"""
        job = self._jobs.get(job_id)
        if not job:
            return None
        return {
            "job_id": job_id,
            "status": job["status"],
            "created_at": job["created_at"],
            "filename": job.get("filename"),
            "result": job.get("result"),
            "error": job.get("error"),
        }

    def get_full(self, job_id: str) -> Optional[Dict[str, Any]]:
        """获取完整任务（含 tmp_path 等，供后台任务使用）"""
        return self._jobs.get(job_id)

    def set_processing(self, job_id: str) -> bool:
        """标记为处理中"""
        if job_id not in self._jobs:
            return False
        self._jobs[job_id]["status"] = STATUS_PROCESSING
        return True

    def set_completed(self, job_id: str, result: Dict[str, Any]) -> bool:
        """标记为完成"""
        if job_id not in self._jobs:
            return False
        self._jobs[job_id]["status"] = STATUS_COMPLETED
        self._jobs[job_id]["result"] = result
        self._jobs[job_id]["error"] = None
        return True

    def set_failed(self, job_id: str, error: str) -> bool:
        """标记为失败"""
        if job_id not in self._jobs:
            return False
        self._jobs[job_id]["status"] = STATUS_FAILED
        self._jobs[job_id]["result"] = None
        self._jobs[job_id]["error"] = error
        return True

    def pop_tmp_path(self, job_id: str) -> Optional[str]:
        """取出并移除 tmp_path（用完后清理）"""
        job = self._jobs.get(job_id)
        if not job:
            return None
        path = job.pop("tmp_path", None)
        return path

    def _maybe_cleanup(self) -> None:
        """超出容量时清理最老的已完成/失败任务"""
        if len(self._jobs) <= MAX_JOBS:
            return
        for jid in list(self._order):
            if len(self._jobs) <= MAX_JOBS:
                break
            job = self._jobs.get(jid)
            if job and job["status"] in (STATUS_COMPLETED, STATUS_FAILED):
                self._jobs.pop(jid, None)
                if jid in self._order:
                    self._order.remove(jid)


# 全局单例
job_store = JobStore()
