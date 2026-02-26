# M28: Dockerfile
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# 安装 Python 3.10、pip 和 ffmpeg（用于 mp3/flac 等音频转码）
RUN apt-get update && \
    apt-get install -y python3.10 python3-pip ffmpeg git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 创建工作目录
WORKDIR /app

# 安装 PyTorch 和其他依赖
RUN pip3 install --no-cache-dir torch==2.1.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cu118 && \
    pip3 install --no-cache-dir fastapi>=0.104.0 uvicorn[standard]>=0.24.0 python-multipart>=0.0.6 pydantic>=2.0.0 pydantic-settings>=2.0.0 pyyaml>=6.0 python-dotenv>=1.0.0 aiofiles>=23.0.0 websockets>=12.0.0 python-json-logger>=2.0.0 psutil>=5.9.0 ffmpeg-python>=0.2.0 transformers>=4.51.3 numpy>=1.26.1 cn2an>=0.5.23 kaldiio>=2.18.0 kaldi_native_fbank>=1.15 sentencepiece>=0.1.99 soundfile>=0.12.1 textgrid>=1.5

# 复制项目文件
# 构建前请先执行: git submodule update --init --recursive
COPY . .

# 暴露 8000 端口
EXPOSE 8000

# 设置启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
