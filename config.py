# SoulLink - 灵犀 AI占卜平台
# 开发环境配置文件

import os
from datetime import timedelta

class Config:
    """基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'soul-link-secret-key-2024'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'soullink_v2.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 会话配置
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # AI API配置 (预留)
    COZE_API_KEY = os.environ.get('COZE_API_KEY', '')
    COZE_API_URL = 'https://api.coze.com/v1/chat'
    COZE_BOT_ID = os.environ.get('COZE_BOT_ID', '')
    
    # 备用LLM配置
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
    OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions'
    
    # 占卜配置
    FREE_DIVINATION_DAILY = 3  # 每日免费占卜次数
    STREAMING_ENABLED = True    # 启用流式输出

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
