#!/usr/bin/env python3
"""手动注册补充路由并启动应用"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 首先导入并配置app
import app as flask_app
from routes_supplementary import register_supplementary_routes

# 注册补充路由
register_supplementary_routes(flask_app.app)
print("补充路由注册成功！")

# 验证路由
print("\n好友系统相关路由:")
for rule in flask_app.app.url_map.iter_rules():
    endpoint = rule.endpoint
    if any(k in endpoint for k in ['friend', 'dm/', 'online']):
        print(f'  {endpoint}: {rule.rule}')

print("\n应用已配置完成，可以启动服务")
