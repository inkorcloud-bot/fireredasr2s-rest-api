"""Punc 模块路由"""

from typing import List, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from core.model_manager import ModelManager
from core.punc_processor import PuncProcessor
from api.deps import get_model_manager
from utils.response_builder import success_response, error_response

router = APIRouter(prefix="/api/v1/modules/punc", tags=["Punc"])


class PuncRequest(BaseModel):
    texts: List[str]
    uttids: List[str] = None


@router.post("/predict")
async def punc_predict(
    req: PuncRequest,
    manager: Optional[ModelManager] = Depends(get_model_manager)
):
    try:
        if not manager:
            return error_response(500, "服务未就绪，模型管理器未初始化")
        processor = PuncProcessor(manager)
        return success_response(await processor.predict(req.texts, req.uttids))
    except Exception as e:
        return error_response(500, str(e))
