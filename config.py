# SoulLink - 灵犀 AI占卜平台
# 生产环境配置文件（支持PostgreSQL/Neon/Zeabur）

import os
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)

class Config:
    """基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'soul-link-secret-key-2024'
    
    # 数据库配置 - 支持多种环境变量格式
    # 1. 优先使用 DATABASE_URL（Neon/手动配置）
    # 2. 其次用 Zeabur PostgreSQL 的独立变量拼接
    # 3. 最后回退到 SQLite（仅本地开发）
    
    @staticmethod
    def _get_database_uri():
        DATABASE_URL = os.environ.get('DATABASE_URL')
        if DATABASE_URL:
            logger.info(f"[DB] Using DATABASE_URL")
            return DATABASE_URL
        
        POSTGRES_HOST = os.environ.get('POSTGRES_HOST')
        if POSTGRES_HOST:
            pg_user = os.environ.get('POSTGRES_USERNAME', 'root')
            pg_pass = os.environ.get('POSTGRES_PASSWORD', '')
            pg_port = os.environ.get('POSTGRES_PORT', '5432')
            pg_db = os.environ.get('POSTGRES_DATABASE', 'root')
            uri = f'postgresql://{pg_user}:{pg_pass}@{POSTGRES_HOST}:{pg_port}/{pg_db}'
            logger.info(f"[DB] Using PostgreSQL from Zeabur: {POSTGRES_HOST}:{pg_port}/{pg_db}")
            return uri
        
        # 回退到 SQLite
        db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'soullink_v2.db')
        logger.info(f"[DB] Falling back to SQLite")
        return 'sqlite:///' + db_path
    
    SQLALCHEMY_DATABASE_URI = property(lambda self: self._get_database_uri())
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 连接池配置（PostgreSQL）
    # 注意：connect_timeout 只对 PostgreSQL 有效
    @staticmethod
    def _get_engine_options():
        options = {
            'pool_size': 2,
            'max_overflow': 5,
            'pool_recycle': 300,
            'pool_pre_ping': True,
            'pool_timeout': 10,
        }
        # 只有 PostgreSQL 支持 connect_timeout
        db_uri = Config._get_database_uri()
        if db_uri.startswith('postgresql'):
            # 在连接URL中加connect_timeout参数
            options['connect_args'] = {}
        return options
    
    SQLALCHEMY_ENGINE_OPTIONS = property(lambda self: self._get_engine_options())
    
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    PORT = int(os.environ.get('PORT', '8080'))
    
    # AI API配置
    COZE_API_KEY = os.environ.get('COZE_API_KEY', '')
    COZE_API_URL = 'https://api.coze.com/v1/chat'
    COZE_BOT_ID = os.environ.get('COZE_BOT_ID', '')
    
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
    OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions'
    
    DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
    DEEPSEEK_API_URL = 'https://api.deepseek.com/v1/chat/completions'
    DEEPSEEK_MODEL = 'deepseek-chat'
    
    FREE_DIVINATION_DAILY = 3
    STREAMING_ENABLED = True

# 在类定义后设置
Config.SQLALCHEMY_DATABASE_URI = Config._get_database_uri()
Config.SQLALCHEMY_ENGINE_OPTIONS = Config._get_engine_options()

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'soullink_v2.db')

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': ProductionConfig
}
