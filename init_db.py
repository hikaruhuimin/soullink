#!/usr/bin/env python3
"""初始化数据库"""

import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# 使用现有app
import app as flask_app
from models import db

with flask_app.app.app_context():
    # 创建所有表
    db.create_all()
    print("数据库表创建成功！")
    
    # 验证表是否存在
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"现有表: {tables}")
    
    # 检查FriendRequest和Friendship表是否存在
    if 'friend_requests' in tables and 'friendships' in tables:
        print("好友系统表已创建")
    else:
        print("好友系统表未创建，可能有问题")
