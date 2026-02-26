#!/bin/bash

# FireRedASR2S REST API Conda 环境设置脚本
# 一键创建 conda 环境

set -e

echo "=========================================="
echo "FireRedASR2S REST API - Conda 环境设置"
echo "=========================================="
echo ""

# 检查 conda 是否安装
if ! command -v conda &> /dev/null; then
    echo "✓ Conda 已安装"
else
    echo "✗ Conda 未安装，请先安装 Miniconda 或 Anaconda"
    exit 1
fi

# 检查 environment.yml 是否存在
if [ ! -f "environment.yml" ]; then
    echo "✗ environment.yml 文件不存在，请在项目根目录运行此脚本"
    exit 1
fi

echo ""
echo "正在创建 Conda 环境 'fireredasr2s'..."
echo "这可能需要几分钟，请耐心等待..."
echo ""

# 创建 conda 环境
conda env create -f environment.yml

echo ""
echo "=========================================="
echo "✓ Conda 环境创建成功！"
echo "=========================================="
echo ""
echo "下一步："
echo "  1. 激活环境：conda activate fireredasr2s"
echo "  2. 初始化子模块（如果还没做）：git submodule update --init --recursive"
echo "  3. 下载模型文件到 pretrained_models/ 目录"
echo "  4. 配置 config.yaml"
echo "  5. 启动服务：python main.py"
echo ""
echo "详细安装步骤请参考 INSTALL.md"
echo ""
