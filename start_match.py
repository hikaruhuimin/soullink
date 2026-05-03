#!/usr/bin/env python3
"""
SoulLink 姻缘匹配功能启动脚本
运行此脚本初始化数据库并启动应用
"""

import os
import sys

def init_match_database():
    """初始化姻缘匹配数据库"""
    from app import app, db
    from models import User
    
    with app.app_context():
        # 创建所有表
        db.create_all()
        print("✅ 数据库表创建成功!")
        
        # 添加新字段到User表（如果不存在）
        try:
            db.session.execute(db.text('''
                ALTER TABLE users ADD COLUMN zodiac_sign VARCHAR(20);
            '''))
            db.session.commit()
            print("✅ 添加 zodiac_sign 字段成功!")
        except Exception as e:
            print(f"⚠️ zodiac_sign 字段: {e}")
        
        try:
            db.session.execute(db.text('''
                ALTER TABLE users ADD COLUMN mbti VARCHAR(10);
            '''))
            db.session.commit()
            print("✅ 添加 mbti 字段成功!")
        except Exception as e:
            print(f"⚠️ mbti 字段: {e}")
        
        try:
            db.session.execute(db.text('''
                ALTER TABLE users ADD COLUMN interests TEXT;
            '''))
            db.session.commit()
            print("✅ 添加 interests 字段成功!")
        except Exception as e:
            print(f"⚠️ interests 字段: {e}")
        
        try:
            db.session.execute(db.text('''
                ALTER TABLE users ADD COLUMN looking_for TEXT;
            '''))
            db.session.commit()
            print("✅ 添加 looking_for 字段成功!")
        except Exception as e:
            print(f"⚠️ looking_for 字段: {e}")
        
        # 创建 likes 表
        try:
            db.session.execute(db.text('''
                CREATE TABLE IF NOT EXISTS likes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_user_id INTEGER NOT NULL,
                    to_user_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (from_user_id) REFERENCES users(id),
                    FOREIGN KEY (to_user_id) REFERENCES users(id),
                    UNIQUE(from_user_id, to_user_id)
                );
            '''))
            db.session.commit()
            print("✅ likes 表创建成功!")
        except Exception as e:
            print(f"⚠️ likes 表: {e}")
        
        # 创建 matches 表
        try:
            db.session.execute(db.text('''
                CREATE TABLE IF NOT EXISTS matches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user1_id INTEGER NOT NULL,
                    user2_id INTEGER NOT NULL,
                    matched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user1_id) REFERENCES users(id),
                    FOREIGN KEY (user2_id) REFERENCES users(id),
                    UNIQUE(user1_id, user2_id)
                );
            '''))
            db.session.commit()
            print("✅ matches 表创建成功!")
        except Exception as e:
            print(f"⚠️ matches 表: {e}")


def register_match_routes():
    """注册姻缘匹配路由"""
    from app import app, db
    
    try:
        from match_routes import register_match_routes as mr
        mr(app, db)
        print("✅ 姻缘匹配路由注册成功!")
        return True
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ 路由注册失败: {e}")
        return False


def start_server():
    """启动服务器"""
    from app import app
    
    print("\n" + "="*50)
    print("🚀 启动 SoulLink 应用...")
    print("="*50)
    
    app.run(host='0.0.0.0', port=5000, debug=True)


def main():
    print("="*50)
    print("SoulLink 姻缘匹配功能初始化")
    print("="*50 + "\n")
    
    # 1. 初始化数据库
    print("📊 步骤1: 初始化数据库...")
    init_match_database()
    
    # 2. 注册路由
    print("\n📝 步骤2: 注册路由...")
    if not register_match_routes():
        print("⚠️ 路由注册失败，但将继续启动...")
    
    # 3. 启动服务器
    print("\n" + "="*50)
    print("✅ 初始化完成!")
    print("="*50)
    print("\n📍 访问地址:")
    print("   - 星座配对: http://localhost:5000/match/zodiac")
    print("   - AI红娘: http://localhost:5000/match/matchmaker")
    print("   - 编辑资料: http://localhost:5000/match/profile/edit")
    print("\n")
    
    start_server()


if __name__ == '__main__':
    main()
