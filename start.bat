@echo off
REM SoulLink - Windows启动脚本

echo 🔮 启动 SoulLink 灵犀 AI占卜平台...

REM 检查依赖
python -c "import flask" 2>nul
if errorlevel 1 (
    echo 📦 正在安装依赖...
    pip install -r requirements.txt
)

REM 确保数据目录存在
if not exist "data" mkdir data

REM 启动应用
echo 🚀 启动服务中...
echo 📍 访问地址: http://localhost:5000
echo.

python app.py
