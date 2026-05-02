#!/usr/bin/env python3
"""添加社交动态和签到系统数据库模型"""

import sys
import os

# 获取脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# 读取models.py
with open('models.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 检查是否已经存在SocialPost模型
if 'class SocialPost' in content:
    print("SocialPost模型已存在，跳过")
else:
    # 在LingStoneTransaction之后插入社交动态和签到模型
    
    social_models = '''

# ============ 社交动态Feed模型 ============

class SocialPost(db.Model):
    """社交动态"""
    __tablename__ = 'social_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # 作者信息
    author_type = db.Column(db.String(20), nullable=False)  # user/agent/system
    author_id = db.Column(db.Integer, nullable=True)  # 对应用户或Agent的ID
    author_name = db.Column(db.String(50), nullable=False)
    author_avatar = db.Column(db.String(200))  # 头像URL
    
    # 动态类型
    post_type = db.Column(db.String(30), nullable=False)  # chat_summary/divination_result/new_agent/friend_milestone/checkin
    
    # 内容
    content = db.Column(db.Text, nullable=False)
    
    # 扩展数据(JSON格式存储额外信息)
    extra_data = db.Column(db.Text)  # 存储为JSON字符串
    
    # 点赞数
    likes_count = db.Column(db.Integer, default=0)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    user_likes = db.relationship('SocialPostLike', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<SocialPost {self.id}: {self.post_type}>'
    
    def get_extra_data(self):
        """获取扩展数据"""
        import json
        if self.extra_data:
            try:
                return json.loads(self.extra_data)
            except:
                return {}
        return {}
    
    def set_extra_data(self, data):
        """设置扩展数据"""
        import json
        self.extra_data = json.dumps(data, ensure_ascii=False)


class SocialPostLike(db.Model):
    """动态点赞记录"""
    __tablename__ = 'social_post_likes'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('social_posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 唯一约束
    __table_args__ = (
        db.UniqueConstraint('post_id', 'user_id', name='unique_post_like'),
    )
    
    def __repr__(self):
        return f'<SocialPostLike {self.post_id} by {self.user_id}>'


# ============ 每日签到模型 ============

class CheckinRecord(db.Model):
    """每日签到记录"""
    __tablename__ = 'checkin_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    checkin_date = db.Column(db.Date, nullable=False)  # 签到日期(仅日期部分)
    streak_days = db.Column(db.Integer, default=1)  # 连续签到天数
    reward_stones = db.Column(db.Integer, default=0)  # 本次获得灵石
    
    # 额外奖励标记
    has_weekly_bonus = db.Column(db.Boolean, default=False)  # 7天连续额外奖励
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref='checkin_records')
    
    # 唯一约束：每天只能签到一次
    __table_args__ = (
        db.UniqueConstraint('user_id', 'checkin_date', name='unique_daily_checkin'),
    )
    
    def __repr__(self):
        return f'<CheckinRecord {self.user_id} @ {self.checkin_date}>'

'''

    # 找到LingStoneTransaction类的结束位置
    import re
    # 在LINGSTONE_PACKAGES常量之前插入模型
    pattern = r"# 灵石充值套餐"
    if re.search(pattern, content):
        content = re.sub(pattern, social_models + "\n" + pattern, content)
        with open('models.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("SocialPost和CheckinRecord模型添加成功！")
    else:
        print("未找到插入位置，请检查models.py结构")


# 检查是否已经存在CheckinRecord模型
if 'class CheckinRecord' in content:
    print("CheckinRecord模型已存在")
