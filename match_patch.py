# 姻缘匹配功能补丁
# 将此文件内容追加到app.py的注册路由部分

# 在 "# Register supplementary routes and lingstone routes" 之后添加以下代码：

"""
    # Register match routes (姻缘匹配)
    try:
        from match_routes import register_match_routes
        from models import db
        register_match_routes(app, db)
    except Exception as e:
        import traceback
        print(f"Warning: Could not register match routes: {e}")
        traceback.print_exc()

"""

# 完整修改步骤：
# 1. 找到 app.py 中 "# Register supplementary routes and lingstone routes" 这行
# 2. 在其后的 try-except 块之后添加上述代码
# 3. 重启应用
