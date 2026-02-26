"""
FireRedASR2S REST API - 主应用入口
工业级语音识别服务
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 导入路由
from api.health import router as health_router
from api.system import router as system_router
from api.admin import router as admin_router
from api.modules.asr import router as asr_router
from api.modules.vad import router as vad_router
from api.modules.lid import router as lid_router
from api.modules.punc import router as punc_router

# 导入核心模块
from core.model_manager import ModelManager
from core.config_loader import load_config
from utils.logger import setup_logger

# 创建应用
app = FastAPI(
    title="FireRedASR2S REST API",
    description="工业级语音识别服务",
    version="1.0.0"
)

# 全局变量
model_manager = None
config = None
logger = None

@app.on_event("startup")
async def startup_event():
    """启动事件：加载配置，初始化模型管理器，预加载模型"""
    global model_manager, config, logger
    logger = setup_logger(__name__)
    logger.info("Starting FireRedASR2S REST API...")
    config = load_config("config.yaml")
    logger.info("Configuration loaded")
    model_manager = ModelManager(config)
    await model_manager.initialize()
    logger.info("FireRedASR2S REST API started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """关闭事件：清理模型资源"""
    global model_manager, logger
    if model_manager:
        await model_manager.cleanup()
        logger.info("Model resources cleaned up")
    logger.info("FireRedASR2S REST API shutdown complete")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# 注册路由
app.include_router(health_router, prefix="/api/v1", tags=["health"])
app.include_router(system_router, prefix="/api/v1", tags=["system"])
app.include_router(admin_router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(asr_router, prefix="/api/v1/modules", tags=["asr"])
app.include_router(vad_router, prefix="/api/v1/modules", tags=["vad"])
app.include_router(lid_router, prefix="/api/v1/modules", tags=["lid"])
app.include_router(punc_router, prefix="/api/v1/modules", tags=["punc"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
