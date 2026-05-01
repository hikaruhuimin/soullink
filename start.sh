#!/bin/bash

# SoulLink - 启动脚本

echo "🔮 启动 SoulLink 灵犀 AI占卜平台..."

# 检查Python版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python版本: $python_version"

# 检查依赖
if ! pip show flask > /dev/null 2>&1; then
    echo "📦 正在安装依赖..."
    pip install -r requirements.txt
fi

# 确保数据目录存在
mkdir -p data

# 启动应用
echo "🚀 启动服务中..."
echo "📍 访问地址: http://localhost:5000"
echo "按 Ctrl+C 停止服务"
echo ""

python3 app.py
