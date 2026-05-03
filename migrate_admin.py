# 数据库迁移脚本
# 运行此脚本添加 is_disabled 字段

import sqlite3
import os

def migrate_database():
    db_path = 'data/soullink_v2.db'
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查 users 表结构
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    
    print(f"Current columns: {columns}")
    
    # 添加 is_disabled 字段
    if 'is_disabled' not in columns:
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN is_disabled BOOLEAN DEFAULT 0")
            conn.commit()
            print("Successfully added is_disabled column!")
        except Exception as e:
            print(f"Error adding column: {e}")
    else:
        print("is_disabled column already exists")
    
    conn.close()

if __name__ == '__main__':
    migrate_database()
