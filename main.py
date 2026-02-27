"""
FireRedASR2S REST API - 主应用入口
工业级语音识别服务
"""
# 将 FireRedASR2S 子模块路径加入 sys.path，确保可正确导入 fireredasr2s
import sys
from pathlib import Path
_submodule_path = Path(__file__).resolve().parent / "FireRedASR2S"
if _submodule_path.exists():
    _path_str = str(_submodule_path)
    if _path_str not in sys.path:
        sys.path.insert(0, _path_str)

# PyTorch 2.6+ 兼容：预训练 checkpoint 含 argparse.Namespace，需加入 safe_globals
import argparse
import torch
torch.serialization.add_safe_globals([argparse.Namespace])

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
from core.asr_system_factory import create_asr_system
from utils.config_loader import load_config
from utils.logger import setup_logger

# 创建应用
app = FastAPI(
    title="FireRedASR2S REST API",
    description="工业级语音识别服务",
    version="1.0.0"
)

# 全局变量
model_manager = None
asr_system = None
config = None
logger = None

@app.on_event("startup")
async def startup_event():
    """启动事件：先创建 FireRedAsr2System，再初始化 ModelManager（从 asr_system 提取独立模块）"""
    global model_manager, asr_system, config, logger
    logger = setup_logger(__name__)
    logger.info("Starting FireRedASR2S REST API...")
    config = load_config("config.yaml")
    logger.info("Configuration loaded")
    models_config = config.get("models", {})

    # 1. 先创建 FireRedAsr2System（当 asr.enabled 时）
    if models_config.get("asr", {}).get("enabled", False):
        try:
            asr_system = create_asr_system(models_config)
            app.state.asr_system = asr_system
            logger.info("FireRedAsr2System 已加载")
        except Exception as e:
            logger.error(f"FireRedAsr2System 加载失败: {e}")
            asr_system = None
            app.state.asr_system = None
    else:
        asr_system = None
        app.state.asr_system = None

    # 2. 初始化 ModelManager，传入 asr_system，独立模块从其中提取
    def on_reload(new_system):
        global asr_system
        asr_system = new_system
        app.state.asr_system = new_system

    model_manager = ModelManager(
        config=models_config,
        asr_system=asr_system,
        on_reload=on_reload
    )
    await model_manager.initialize()
    app.state.model_manager = model_manager

    logger.info("FireRedASR2S REST API started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """关闭事件：清理模型资源"""
    global model_manager, asr_system, logger
    if model_manager:
        await model_manager.cleanup()
        logger.info("Model resources cleaned up")
    asr_system = None
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
    import argparse

    # 硬编码默认值（最低优先级）
    DEFAULT_HOST = "0.0.0.0"
    DEFAULT_PORT = 8000

    # 从 config.yaml 读取配置（次优先级）
    config_from_yaml = load_config("config.yaml")
    server_config = config_from_yaml.get('server', {})
    host = server_config.get('host', DEFAULT_HOST)
    port = server_config.get('port', DEFAULT_PORT)

    # 解析命令行参数（最高优先级）
    parser = argparse.ArgumentParser(description="FireRedASR2S REST API Server")
    parser.add_argument("--host", type=str, default=host, 
                        help=f"Host to bind to (default: {host} from config.yaml)")
    parser.add_argument("--port", type=int, default=port, 
                        help=f"Port to bind to (default: {port} from config.yaml)")
    args = parser.parse_args()

    # 命令行参数优先级最高
    host = args.host
    port = args.port

    uvicorn.run(app, host=host, port=port)
