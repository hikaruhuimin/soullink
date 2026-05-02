#!/usr/bin/env python3
"""修改app.py添加Agent API路由注册"""

import os

# 读取app.py
script_dir = os.path.dirname(os.path.abspath(__file__))
app_path = os.path.join(script_dir, 'app.py')

with open(app_path, 'r', encoding='utf-8') as f:
    content = f.read()
if 'register_agent_api_routes' in content:
    print("register_agent_api_routes 已存在，跳过")
else:
    # 在register_supplementary_routes调用后添加新路由注册
    # 查找 "register_lingstone_routes(app, db)" 并在其后添加新代码
    
    old_text = """    # Register supplementary routes and lingstone routes
    try:
        from routes_supplementary import register_supplementary_routes, register_lingstone_routes
        register_supplementary_routes(app)
        register_lingstone_routes(app, db)
    except Exception as e:
        import traceback
        print(f"Warning: Could not register routes: {e}")
        traceback.print_exc()"""
    
    new_text = """    # Register supplementary routes and lingstone routes
    try:
        from routes_supplementary import register_supplementary_routes, register_lingstone_routes, register_agent_api_routes
        register_supplementary_routes(app)
        register_lingstone_routes(app, db)
        register_agent_api_routes(app, db)
    except Exception as e:
        import traceback
        print(f"Warning: Could not register routes: {e}")
        traceback.print_exc()"""
    
    content = content.replace(old_text, new_text)
    
    # 写回
    with open('./soullink/app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("已添加 register_agent_api_routes 调用")

print("完成")
