#!/usr/bin/env python3
"""修改app.py添加Agent API路由注册 - 二进制版本"""

import os

script_dir = os.path.dirname(os.path.abspath(__file__))
app_path = os.path.join(script_dir, 'app.py')

# 以二进制读取
with open(app_path, 'rb') as f:
    content = f.read()

# 检查是否已注册
if b'register_agent_api_routes' in content:
    print("register_agent_api_routes 已存在，跳过")
else:
    # 找到register_supplementary_routes的位置
    old_pattern = b'register_supplementary_routes, register_lingstone_routes'
    
    if old_pattern in content:
        # 替换为包含register_agent_api_routes的版本
        new_pattern = b'register_supplementary_routes, register_lingstone_routes, register_agent_api_routes'
        content = content.replace(old_pattern, new_pattern)
        
        # 同时更新import
        import_pattern = b'from routes_supplementary import register_supplementary_routes, register_lingstone_routes'
        new_import = b'from routes_supplementary import register_supplementary_routes, register_lingstone_routes, register_agent_api_routes'
        content = content.replace(import_pattern, new_import)
        
        # 写回
        with open(app_path, 'wb') as f:
            f.write(content)
        print("已添加 register_agent_api_routes")
    else:
        print("未找到目标模式，尝试其他方式...")
        # 尝试另一种模式
        old_pattern2 = b'register_lingstone_routes(app, db)'
        if old_pattern2 in content:
            new_content = b'register_lingstone_routes(app, db)\n        register_agent_api_routes(app, db)'
            content = content.replace(old_pattern2, new_content)
            
            # 更新import
            import_pattern2 = b'from routes_supplementary import register_supplementary_routes, register_lingstone_routes'
            new_import2 = b'from routes_supplementary import register_supplementary_routes, register_lingstone_routes, register_agent_api_routes'
            content = content.replace(import_pattern2, new_import2)
            
            with open(app_path, 'wb') as f:
                f.write(content)
            print("已添加 register_agent_api_routes (方式2)")
        else:
            print("未找到合适的位置插入代码")

print("完成")
