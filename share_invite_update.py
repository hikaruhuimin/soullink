"""
分享卡片 + 邀请码系统 - 数据库模型更新
"""
import sys
sys.path.insert(0, '/tmp/soullink')

from models import db
from sqlalchemy import text
import random
import string

def generate_invite_code():
    """生成8位邀请码"""
    chars = string.ascii_uppercase + string.digits
    return 'SL' + ''.join(random.choices(chars, k=6))

def upgrade_database():
    """更新数据库结构"""
    print("开始数据库升级...")
    
    # 1. 为 users 表添加 invite_code 字段
    try:
        db.session.execute(text("ALTER TABLE users ADD COLUMN invite_code VARCHAR(10)"))
        db.session.commit()
        print("✓ users 表添加 invite_code 字段成功")
    except Exception as e:
        if 'duplicate column' in str(e).lower() or 'already exists' in str(e).lower():
            print("○ invite_code 字段已存在，跳过")
        else:
            print(f"△ users 表字段检查: {e}")
    
    # 2. 创建 invitations 表
    try:
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS invitations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inviter_id INTEGER NOT NULL,
                invitee_id INTEGER NOT NULL,
                reward INTEGER DEFAULT 50,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (inviter_id) REFERENCES users(id),
                FOREIGN KEY (invitee_id) REFERENCES users(id)
            )
        """))
        db.session.commit()
        print("✓ invitations 表创建成功")
    except Exception as e:
        if 'already exists' in str(e).lower():
            print("○ invitations 表已存在，跳过")
        else:
            print(f"△ invitations 表检查: {e}")
    
    # 3. 为已有用户生成邀请码
    try:
        from models import User
        users_without_code = User.query.filter(
            (User.invite_code == None) | (User.invite_code == '')
        ).all()
        
        for user in users_without_code:
            user.invite_code = generate_invite_code()
        
        db.session.commit()
        print(f"✓ 为 {len(users_without_code)} 个用户生成邀请码")
    except Exception as e:
        print(f"△ 生成邀请码检查: {e}")
        db.session.rollback()
    
    print("\n数据库升级完成!")

if __name__ == '__main__':
    upgrade_database()
