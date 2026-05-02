#!/usr/bin/env python3
"""修改app.py以调用register_supplementary_routes"""

import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# 读取app.py的字节码并搜索关键字符串
with open('app.py', 'rb') as f:
    content = f.read()

# 检查是否已经导入了routes_supplementary
if b'routes_supplementary' not in content:
    # 找到 import 语句附近的位置
    # 搜索 "from flask import" 或类似的导入语句
    
    # 创建一个简单的Python脚本来处理
    print("需要修改app.py二进制文件")
    print("由于app.py是二进制文件，我们将创建一个包装脚本来启动应用")

# 创建wsgi.py包装文件
wsgi_content = '''#!/usr/bin/env python3
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
'''

with open('wsgi.py', 'w') as f:
    f.write(wsgi_content)

print("wsgi.py创建成功！")
print("请使用以下命令启动gunicorn:")
print("  gunicorn -w 2 -b 0.0.0.0:5000 --timeout 120 wsgi:application")
