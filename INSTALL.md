# FireRedASR2S REST API 安装指南

## 环境要求

- Python 3.10+
- CUDA 11.8+ (如果使用 GPU)
- **FFmpeg**（用于非 WAV 音频转码，如 mp3/flac 等）：`sudo apt install ffmpeg` (Ubuntu/Debian)
- **Conda**（推荐使用 Miniconda 或 Anaconda）

## 安装步骤

### 方式一：使用 Conda（推荐）

#### 1. 克隆项目并初始化子模块

```bash
git clone <repository-url>
cd fireredasr2s-rest-api

# 初始化 FireRedASR2S 子模块（必需）
git submodule update --init --recursive
```

#### 2. 创建并激活 Conda 环境

```bash
# 使用 environment.yml 创建环境（包含 Python 3.10、PyTorch 2.1.0 CUDA 11.8 及所有依赖）
conda env create -f environment.yml

# 激活环境
conda activate fireredasr2s
```

#### 3. 继续步骤 4 准备模型文件...

---

### 方式二：使用 pip

#### 1. 克隆项目并初始化子模块

```bash
git clone <repository-url>
cd fireredasr2s-rest-api

# 初始化 FireRedASR2S 子模块（必需）
git submodule update --init --recursive
```

#### 2. 安装 PyTorch（重要！）

PyTorch 需要根据你的环境手动安装，因为 CPU 和 GPU 版本不同。

##### CPU 版本（无 GPU）

```bash
pip install torch==2.1.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cpu
```

##### GPU 版本（CUDA 11.8）

```bash
pip install torch==2.1.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cu118
```

##### GPU 版本（CUDA 12.1）

```bash
pip install torch==2.1.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cu121
```

##### 其他版本

访问 [PyTorch 官网](https://pytorch.org/get-started/locally/) 获取适合你系统的安装命令。

#### 3. 安装其他依赖

```bash
pip install -r requirements.txt
```

### 4. 准备模型文件

将 FireRedASR2S 的模型文件下载到对应的目录：

```
pretrained_models/
├── FireRedASR2-AED/          # ASR 模型（AED）
├── FireRedASR2-LLM/          # ASR 模型（LLM，可选）
├── FireRedVAD/
│   ├── VAD/                  # VAD 模型
│   ├── Stream-VAD/           # 流式 VAD 模型
│   └── AED/                  # AED 模型
├── FireRedLID/               # 语种识别模型
└── FireRedPunc/              # 标点预测模型
```

### 5. 配置模型路径

编辑 `config.yaml`，根据实际模型路径修改配置：

```yaml
models:
  preload_on_start: true

  asr:
    enabled: true
    type: "aed"  # aed 或 llm
    model_dir: "./pretrained_models/FireRedASR2-AED"
    use_gpu: false  # 设置为 true 如果有 GPU
    use_half: false
    beam_size: 3

  # ... 其他配置
```

### 6. 启动服务

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 验证安装

访问健康检查端点：

```bash
curl http://localhost:8000/api/v1/health
```

## 常见问题

### ImportError: No module named 'torch'

**原因**：PyTorch 未安装

**解决**：按照步骤 2 安装 PyTorch

### CUDA out of memory

**原因**：GPU 内存不足

**解决**：
- 减少批处理大小
- 在 config.yaml 中设置 `use_half: true` 使用半精度
- 切换到 CPU 模式（性能会降低）

### 模型文件未找到

**原因**：模型路径配置错误或模型文件未下载

**解决**：
- 检查 config.yaml 中的 model_dir 路径
- 确保模型文件已正确下载到对应目录
