"""Punc 模块路由"""

from fastapi import APIRouter
from typing import List
from pydantic import BaseModel
from core.punc_processor import PuncProcessor
from utils.response_builder import success_response, error_response

router = APIRouter(prefix="/api/v1/modules/punc", tags=["Punc"])


class PuncRequest(BaseModel):
    texts: List[str]
    uttids: List[str] = None


@router.post("/predict")
async def punc_predict(req: PuncRequest):
    try:
        return success_response(await PuncProcessor.predict(req.texts, req.uttids))
    except Exception as e:
        return error_response(500, str(e))
