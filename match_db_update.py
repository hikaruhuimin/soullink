# 数据库更新脚本 - 添加姻缘匹配相关表和字段

from models import db
from datetime import datetime


def upgrade_database():
    """升级数据库"""
    
    # 1. 添加 User 表的新字段 (使用原始 SQL 因为 SQLAlchemy 的 alter 不太方便)
    try:
        db.session.execute(db.text('''
            ALTER TABLE users ADD COLUMN zodiac_sign VARCHAR(20);
        '''))
    except Exception as e:
        print(f"zodiac_sign column may already exist: {e}")
    
    try:
        db.session.execute(db.text('''
            ALTER TABLE users ADD COLUMN mbti VARCHAR(10);
        '''))
    except Exception as e:
        print(f"mbti column may already exist: {e}")
    
    try:
        db.session.execute(db.text('''
            ALTER TABLE users ADD COLUMN interests TEXT;
        '''))
    except Exception as e:
        print(f"interests column may already exist: {e}")
    
    try:
        db.session.execute(db.text('''
            ALTER TABLE users ADD COLUMN looking_for TEXT;
        '''))
    except Exception as e:
        print(f"looking_for column may already exist: {e}")
    
    # 2. 创建 likes 表（心动记录）
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
    except Exception as e:
        print(f"likes table may already exist: {e}")
    
    # 3. 创建 matches 表（配对记录）
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
    except Exception as e:
        print(f"matches table may already exist: {e}")
    
    # 4. 创建 zodiac_compatibility_cache 表（星座配对缓存）
    try:
        db.session.execute(db.text('''
            CREATE TABLE IF NOT EXISTS zodiac_compatibility_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                zodiac1 VARCHAR(20) NOT NULL,
                zodiac2 VARCHAR(20) NOT NULL,
                overall_score INTEGER,
                love_score INTEGER,
                career_score INTEGER,
                analysis_zh TEXT,
                advice_zh TEXT,
                analysis_en TEXT,
                advice_en TEXT,
                analysis_ja TEXT,
                advice_ja TEXT,
                UNIQUE(zodiac1, zodiac2)
            );
        '''))
    except Exception as e:
        print(f"zodiac_compatibility_cache table may already exist: {e}")
    
    # 5. 创建 zodiac_match_history 表（配对历史）
    try:
        db.session.execute(db.text('''
            CREATE TABLE IF NOT EXISTS zodiac_match_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                zodiac1 VARCHAR(20) NOT NULL,
                zodiac2 VARCHAR(20) NOT NULL,
                result_score INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        '''))
    except Exception as e:
        print(f"zodiac_match_history table may already exist: {e}")
    
    db.session.commit()
    print("Database upgrade completed!")


def downgrade_database():
    """降级数据库（回滚）"""
    try:
        db.session.execute(db.text('ALTER TABLE users DROP COLUMN zodiac_sign;'))
    except:
        pass
    
    try:
        db.session.execute(db.text('ALTER TABLE users DROP COLUMN mbti;'))
    except:
        pass
    
    try:
        db.session.execute(db.text('ALTER TABLE users DROP COLUMN interests;'))
    except:
        pass
    
    try:
        db.session.execute(db.text('ALTER TABLE users DROP COLUMN looking_for;'))
    except:
        pass
    
    try:
        db.session.execute(db.text('DROP TABLE IF EXISTS likes;'))
    except:
        pass
    
    try:
        db.session.execute(db.text('DROP TABLE IF EXISTS matches;'))
    except:
        pass
    
    try:
        db.session.execute(db.text('DROP TABLE IF EXISTS zodiac_compatibility_cache;'))
    except:
        pass
    
    try:
        db.session.execute(db.text('DROP TABLE IF EXISTS zodiac_match_history;'))
    except:
        pass
    
    db.session.commit()
    print("Database downgrade completed!")


if __name__ == '__main__':
    from app import app
    with app.app_context():
        upgrade_database()
