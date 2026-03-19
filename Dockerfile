# M28: Dockerfile
FROM nvidia/cuda:12.6.2-cudnn-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive \
    CONDA_DIR=/opt/conda \
    PATH=/opt/conda/bin:$PATH

# 安装 Miniconda 所需的系统工具
RUN apt-get update && \
    apt-get install -y --no-install-recommends wget bzip2 ca-certificates git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 安装 Miniconda，后续统一通过 environment.yml 管理依赖
RUN wget -qO /tmp/miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    bash /tmp/miniconda.sh -b -p "$CONDA_DIR" && \
    rm -f /tmp/miniconda.sh && \
    conda clean -afy

# 创建工作目录
WORKDIR /app

# 先复制环境文件，尽量利用 Docker 构建缓存
COPY environment.yml ./

RUN conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main && \
    conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r && \
    conda env create -f environment.yml && \
    conda clean -afy

# 复制项目文件
# 构建前请先执行: git submodule update --init --recursive
COPY . .

# 暴露 8000 端口
EXPOSE 8000

# 使用 conda 环境启动服务
CMD ["conda", "run", "--no-capture-output", "-n", "fireredasr2s", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
