#!/usr/bin/env python3
"""添加UserAgent模型到models.py"""

import os

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# 读取models.py
with open('models.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 检查是否已存在UserAgent模型
if 'class UserAgent(db.Model):' in content:
    print("UserAgent模型已存在，跳过添加")
    exit(0)

# UserAgent模型定义
user_agent_model = '''

class UserAgent(db.Model):
    """用户创建的Agent"""
    __tablename__ = 'user_agents'
    
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    mbti = db.Column(db.String(4))  # MBTI类型
    personality = db.Column(db.Text)  # 性格描述
    specialty = db.Column(db.String(200))  # 专长/技能（JSON格式存储多个技能）
    greeting = db.Column(db.Text)  # 开场白
    avatar = db.Column(db.String(500))  # 头像URL
    
    # 状态
    is_active = db.Column(db.Boolean, default=True)
    
    # 统计
    chat_count = db.Column(db.Integer, default=0)  # 互动次数
    earned_stones = db.Column(db.Integer, default=0)  # 赚取的灵石
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    owner = db.relationship('User', backref='user_agents')
    
    def __repr__(self):
        return f'<UserAgent {self.name}>'
    
    def get_specialty_list(self):
        """获取专长列表"""
        if not self.specialty:
            return []
        try:
            import json
            return json.loads(self.specialty)
        except:
            return [self.specialty] if self.specialty else []
    
    def set_specialty_list(self, specialty_list):
        """设置专长列表"""
        import json
        self.specialty = json.dumps(specialty_list)
'''

# 在AgentChat模型之前添加
insert_point = "class AgentChat(db.Model):"
if insert_point in content:
    content = content.replace(insert_point, user_agent_model + insert_point)
    with open('models.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("UserAgent模型添加成功！")
else:
    print("未找到插入点，添加失败")
