#!/usr/bin/env python3
"""添加RegisteredAgent模型到models.py"""

import os
import sys

# 读取现有models.py
script_dir = os.path.dirname(os.path.abspath(__file__))
models_path = os.path.join(script_dir, 'models.py')

with open(models_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 检查是否已存在RegisteredAgent模型
if 'class RegisteredAgent' in content:
    print("RegisteredAgent模型已存在，跳过添加")
    sys.exit(0)

# 定义要添加的模型代码
model_code = '''


# ============ 注册Agent模型（API注册） ============

class RegisteredAgent(db.Model):
    """通过API注册的外部Agent"""
    __tablename__ = 'registered_agents'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # 基本身份
    agent_name = db.Column(db.String(50), nullable=False)  # Agent名字
    api_key = db.Column(db.String(64), unique=True, nullable=False)  # API密钥（自动生成）
    platform = db.Column(db.String(50))  # 来源平台：coze/agentlink/custom
    
    # 人设信息
    mbti = db.Column(db.String(4))  # MBTI类型
    personality = db.Column(db.Text)  # 性格描述
    specialties = db.Column(db.String(500))  # 专长（JSON数组）
    greeting = db.Column(db.Text)  # 开场白
    avatar_url = db.Column(db.String(500))  # 头像URL
    
    # 通信
    callback_url = db.Column(db.String(500))  # 聊天消息回调URL
    webhook_secret = db.Column(db.String(64))  # webhook签名密钥
    
    # 统计
    chat_count = db.Column(db.Integer, default=0)  # 聊天次数
    rating = db.Column(db.Float, default=5.0)  # 评分
    earned_stones = db.Column(db.Integer, default=0)  # 赚取灵石
    
    # 状态
    is_active = db.Column(db.Boolean, default=True)  # 是否在线
    is_verified = db.Column(db.Boolean, default=False)  # 是否认证
    
    # 时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_specialties_list(self):
        """获取专长列表"""
        if not self.specialties:
            return []
        try:
            import json
            return json.loads(self.specialties)
        except:
            return [self.specialties] if self.specialties else []
    
    def to_dict(self):
        """转换为字典"""
        return {
            'agent_id': self.id,
            'agent_name': self.agent_name,
            'platform': self.platform,
            'mbti': self.mbti,
            'personality': self.personality,
            'specialties': self.get_specialties_list(),
            'greeting': self.greeting,
            'avatar_url': self.avatar_url,
            'chat_count': self.chat_count,
            'rating': round(self.rating, 1) if self.rating else 5.0,
            'earned_stones': self.earned_stones,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

'''

# 添加模型到文件末尾
new_content = content + model_code

# 写回文件
with open(models_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"成功添加RegisteredAgent模型到 {models_path}")
