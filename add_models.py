#!/usr/bin/env python3
"""添加SocialPost和CheckinRecord模型到models.py"""

import sys

# 要添加的模型代码
new_models = '''

# ============ 动态Feed模型 ============
class FeedPost(db.Model):
    """动态Feed帖子"""
    __tablename__ = 'feed_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    author_type = db.Column(db.String(10), nullable=False)  # user/agent/system
    author_id = db.Column(db.Integer)
    author_name = db.Column(db.String(50))
    author_avatar = db.Column(db.String(500))
    post_type = db.Column(db.String(30))  # chat_summary/divination_result/new_agent/friend_milestone/checkin
    content = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    likes_count = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 点赞关系
    likes = db.relationship('FeedPostLike', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    
    def is_liked_by(self, user_id):
        """检查用户是否已点赞"""
        return self.likes.filter_by(user_id=user_id).first() is not None


class FeedPostLike(db.Model):
    """动态点赞记录"""
    __tablename__ = 'feed_post_likes'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('feed_posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('post_id', 'user_id', name='unique_post_like'),)


# ============ 每日签到模型 ============
# 签到奖励配置
CHECKIN_REWARDS = [
    {'day': 1, 'stones': 10},
    {'day': 2, 'stones': 15},
    {'day': 3, 'stones': 20},
    {'day': 4, 'stones': 25},
    {'day': 5, 'stones': 30},
    {'day': 6, 'stones': 40},
    {'day': 7, 'stones': 50},
]
CHECKIN_WEEKLY_BONUS = 100


class CheckinRecord(db.Model):
    """每日签到记录"""
    __tablename__ = 'checkin_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    checkin_date = db.Column(db.Date, nullable=False)
    streak_days = db.Column(db.Integer, default=1)
    reward_stones = db.Column(db.Integer, default=0)
    has_weekly_bonus = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='checkin_records')
    
    __table_args__ = (db.UniqueConstraint('user_id', 'checkin_date', name='unique_daily_checkin'),)
'''

# 读取models.py
with open('models.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 检查是否已存在FeedPost模型
if 'class FeedPost' in content:
    print("FeedPost模型已存在，跳过")
else:
    # 在文件末尾追加新模型
    with open('models.py', 'a', encoding='utf-8') as f:
        f.write(new_models)
    print("成功添加FeedPost、FeedPostLike、CheckinRecord模型到models.py")

print("models.py修改完成")
