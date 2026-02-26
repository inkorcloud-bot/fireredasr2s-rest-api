"""
Cursor 开发任务：创建 M26 (main.py) 和 M27 (__init__.py 文件)
"""

task = """
请创建以下文件：

## 1. main.py (应用入口)
创建 fireredasr2s-rest-api/main.py 文件，要求：

1. 创建 FastAPI 应用实例
2. 注册所有路由（health, system, admin, modules: asr, vad, lid, punc）
3. 添加启动事件（加载配置、初始化模型管理器、预加载模型）
4. 添加关闭事件（清理模型资源）
5. 配置 CORS（跨域支持）
6. 添加应用元数据（title="FireRedASR2S REST API", description="工业级语音识别服务", version="1.0.0"）
7. 代码量控制在 80 行以内

参考结构：
```python
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
from core.config_loader import load_config
from core.model_manager import ModelManager
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

@app.on_event("shutdown")
async def shutdown_event():
    """关闭事件：清理模型资源"""

# CORS配置
app.add_middleware(CORSMiddleware, allow_origins=["*"], ...)

# 注册路由
app.include_router(health_router, prefix="/api/v1", tags=["health"])
app.include_router(system_router, prefix="/api/v1", tags=["system"])
app.include_router(admin_router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(asr_router, prefix="/api/v1/modules", tags=["["asr"])
app.include_router(vad_router, prefix="/api/v1/modules", tags=["vad"])
app.include_router(lid_router, prefix="/api/v1/modules", tags=["lid"])
app.include_router(punc_router, prefix="/api/v1/modules", tags=["punc"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 2. __init__.py 文件 (包初始化)
创建以下 __init__.py 文件：

- fireredasr2s-rest-api/core/__init__.py: 导出 ModelManager 等核心类
- fireredasr2s-rest-api/schemas/__init__.py: 导出响应和请求模型
- fireredasr2s-rest-api/utils/__init__.py: 导出工具函数（logger等）

请先查看已有的模块文件，了解导出的类和函数，然后创建相应的 __init__.py 文件。

工作目录：/home/node/.openclaw/workspace/fireredasr2s-rest-api
"""
