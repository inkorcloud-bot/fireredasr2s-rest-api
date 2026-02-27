# FireRedASR2S REST API

## 项目简介

FireRedASR2S REST API 是一个基于 FastAPI 构建的语音识别 REST 服务，提供高效的 ASR（自动语音识别）功能。该服务支持 VAD（语音活动检测）、LID（语言识别）、标点恢复等功能，并采用异步处理以提高性能。

## 功能特性

- **ASR（自动语音识别）**：支持实时语音转文字
- **VAD（语音活动检测）**：智能检测语音段落
- **LID（语言识别）**：识别语音的语言类型
- **标点恢复**：为识别结果添加标点符号
- **异步处理**：基于 FastAPI 的异步架构
- **GPU 加速**：支持 NVIDIA CUDA 加速
- **系统监控**：提供资源使用情况查询
- **健康检查**：内置健康检查端点
- **配置管理**：支持 YAML 和 ENV 配置
- **多格式音频**：支持 wav/mp3/flac/ogg/m4a，非 WAV 自动转码为 16kHz 16-bit mono PCM

## 安装部署说明

### 环境要求

- Python 3.10
- PyTorch 2.1.0 + torchaudio 2.1.0 (CUDA 11.8)
- Conda（推荐使用 Miniconda 或 Anaconda）
- FFmpeg（使用 conda 会自动安装）

### 快速启动

**⚠️ 重要：详细的安装步骤请参考 [INSTALL.md](INSTALL.md)**

#### 方式一：使用 Conda（推荐）

1. **克隆项目并初始化子模块**
   ```bash
   git clone <repository-url>
   cd fireredasr2s-rest-api
   git submodule update --init --recursive  # 初始化 FireRedASR2S 子模块
   ```

2. **创建并激活 Conda 环境**
   ```bash
   conda env create -f environment.yml
   conda activate fireredasr2s
   ```

3. **继续配置模型文件...**（详见 INSTALL.md）

---

#### 方式二：使用 pip

1. **克隆项目并初始化子模块**
   ```bash
   git clone <repository-url>
   cd fireredasr2s-rest-api
   git submodule update --init --recursive  # 初始化 FireRedASR2S 子模块
   ```

2. **安装 PyTorch（根据环境手动安装）**

   CPU 版本：
   ```bash
   pip install torch==2.1.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cpu
   ```

   GPU 版本（CUDA 11.8）：
   ```bash
   pip install torch==2.1.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cu118
   ```

3. **安装其他依赖**
   ```bash
   pip install fastapi>=0.104.0 uvicorn[standard]>=0.24.0 python-multipart>=0.0.6 pydantic>=2.0.0 pydantic-settings>=2.0.0 pyyaml>=6.0 python-dotenv>=1.0.0 aiofiles>=23.0.0 websockets>=12.0.0 python-json-logger>=2.0.0 psutil>=5.9.0 ffmpeg-python>=0.2.0 transformers>=4.51.3 numpy>=1.26.1 cn2an>=0.5.23 kaldiio>=2.18.0 kaldi_native_fbank>=1.15 sentencepiece>=0.1.99 soundfile>=0.12.1 textgrid>=1.5
   ```

4. **下载模型**
   ```bash
   # 将模型文件放置到 pretrained_models/ 目录
   # 详见 INSTALL.md
   ```

5. **配置模型路径**
   ```bash
   # 编辑 config.yaml，设置正确的模型路径
   ```

6. **启动服务**

### 配置优先级
- **命令行参数**（最高优先级）：`--host=0.0.0.0 --port=8000`
- **config.yaml**（次优先级）：server.host 和 server.port
- **硬编码默认值**（最低优先级）：host=0.0.0.0, port=8000

### 默认启动（使用 config.yaml 配置）
```bash
python main.py
```

### 指定端口（命令行参数优先）
```bash
python main.py --port=9000
```

### 指定 host 和 port
```bash
python main.py --host=127.0.0.1 --port=9000
```

### 使用 uvicorn 直接启动
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Docker 部署（可选）

**构建前请先初始化子模块**：`git submodule update --init --recursive`

如果使用 Docker 部署：

- Docker 20.10+
- Docker Compose 2.0+
- NVIDIA Driver（支持 CUDA 11.8）
- NVIDIA Container Toolkit

```bash
docker-compose up -d
docker-compose logs -f
```

停止服务：
```bash
docker-compose down
```

## 配置说明

### 环境变量（.env）

| 变量名 | 说明 | 示例 |
|--------|------|------|
| HOST | 服务监听地址 | 0.0.0.0 |
| PORT | 服务监听端口 | 8000 |
| MODEL_PATH | 模型文件路径 | /app/models |
| MAX_AUDIO_SIZE | 最大音频文件大小（MB） | 50 |
| WORKER_THREADS | 工作线程数 | 4 |

### 配置文件（config.yaml）

```yaml
model:
  asr:
    path: "/app/models/asr_model.bin"
  vad:
    path: "/app/models/vad_model.bin"
  lid:
    path: "/app/models/lid_model.bin"

server:
  host: "0.0.0.0"
  port: 8000
  workers: 4
```

## API 使用示例

### 健康检查

```bash
curl http://localhost:8000/health
```

### ASR 识别

```bash
curl -X POST http://localhost:8000/api/v1/asr/transcribe \
  -H "Content-Type: multipart/form-data" \
  -F "file=@audio.wav" \
  -F "language=zh"
```

### WebSocket 实时识别

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/asr/stream');

ws.onopen = () => {
  console.log('Connected');
};

ws.onmessage = (event) => {
  console.log('Result:', event.data);
};

// 发送音频数据
ws.send(audioData);
```

### 异步转录（长音频推荐）

适用于 1 小时以上的会议录音等，避免 HTTP 超时：

```bash
# 1. 提交任务，立即获得 job_id
JOB_ID=$(curl -s -X POST http://localhost:8000/api/v1/system/transcribe/submit \
  -F "audio=@meeting.aac" | jq -r '.data.job_id')

# 2. 轮询状态
curl "http://localhost:8000/api/v1/system/transcribe/status/$JOB_ID"

# 3. 完成后获取结果
curl "http://localhost:8000/api/v1/system/transcribe/result/$JOB_ID"
```

状态说明：`pending` → `processing` → `completed` 或 `failed`

### 系统状态查询

```bash
curl http://localhost:8000/api/v1/system/status
```

### 管理接口

```bash
# 重载配置
curl -X POST http://localhost:8000/api/v1/admin/reload-config

# 清理缓存
curl -X POST http://localhost:8000/api/v1/admin/clear-cache
```

## 开发指南

### 本地开发

#### 使用 Conda（推荐）

1. **创建并激活环境**
   ```bash
   conda env create -f environment.yml
   conda activate fireredasr2s
   ```

2. **启动开发服务器**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

---

#### 使用 pip

1. **安装 PyTorch（根据环境）**

   CPU 版本：
   ```bash
   pip install torch==2.1.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cpu
   ```

   GPU 版本（CUDA 11.8）：
   ```bash
   pip install torch==2.1.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cu118
   ```

2. **安装其他依赖**
   ```bash
   pip install fastapi>=0.104.0 uvicorn[standard]>=0.24.0 python-multipart>=0.0.6 pydantic>=2.0.0 pydantic-settings>=2.0.0 pyyaml>=6.0 python-dotenv>=1.0.0 aiofiles>=23.0.0 websockets>=12.0.0 python-json-logger>=2.0.0 psutil>=5.9.0 ffmpeg-python>=0.2.0 transformers>=4.51.3 numpy>=1.26.1 cn2an>=0.5.23 kaldiio>=2.18.0 kaldi_native_fbank>=1.15 sentencepiece>=0.1.99 soundfile>=0.12.1 textgrid>=1.5
   ```

3. **启动开发服务器**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### 项目结构

```
fireredasr2s-rest-api/
├── FireRedASR2S/           # FireRedASR2S 子模块（git submodule）
├── api/                    # API 路由
│   ├── modules/           # 功能模块
│   │   ├── asr.py         # ASR 识别
│   │   ├── vad.py         # 语音检测
│   │   ├── lid.py         # 语言识别
│   │   └── punc.py        # 标点恢复
│   ├── admin.py           # 管理接口
│   ├── health.py          # 健康检查
│   └── system.py          # 系统状态
├── core/                   # 核心逻辑
├── models/                 # 模型文件
├── schemas/               # 数据验证
├── utils/                 # 工具函数
├── config.yaml            # 配置文件
├── environment.yml        # Conda 环境配置
├── setup_conda.sh         # Conda 环境一键设置脚本
├── Dockerfile             # Docker 构建文件
└── docker-compose.yml     # Docker Compose 配置
```

### 代码规范

- 使用 Black 格式化代码
- 使用 Pylint 进行代码检查
- 遵循 PEP 8 规范
- 编写单元测试

### 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

MIT License

## 联系方式

- 项目地址：[GitHub Repository]
- 问题反馈：[Issues]
