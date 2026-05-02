#!/usr/bin/env python3
"""WSGI包装器 - 在启动前注册补充路由"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 首先导入并配置app
import app as flask_app
from routes_supplementary import register_supplementary_routes

# 注册补充路由
register_supplementary_routes(flask_app.app)

# 导出app供gunicorn使用
application = flask_app.app

if __name__ == "__main__":
    flask_app.app.run(host="0.0.0.0", port=5000, debug=True)
