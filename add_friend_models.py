#!/usr/bin/env python3
"""添加好友系统数据库模型"""

import sys
import os

# 获取脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# 读取models.py
with open('models.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 检查是否已经存在FriendRequest和Friendship模型
if 'class FriendRequest' in content:
    print("FriendRequest模型已存在，跳过")
else:
    # 在LingStoneRecharge之前插入好友模型
    
    friend_models = '''

# ============ 好友系统模型 ============

class FriendRequest(db.Model):
    """好友请求"""
    __tablename__ = 'friend_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 状态: pending(待处理), accepted(已接受), rejected(已拒绝)
    status = db.Column(db.String(20), default='pending')
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_friend_requests')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_friend_requests')
    
    def __repr__(self):
        return f'<FriendRequest {self.id}: {self.sender_id} -> {self.receiver_id}>'


class Friendship(db.Model):
    """好友关系"""
    __tablename__ = 'friendships'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 备注
    friend_nickname = db.Column(db.String(50))
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', foreign_keys=[user_id], backref='friendships')
    friend = db.relationship('User', foreign_keys=[friend_id], backref='friend_of')
    
    # 唯一约束：防止重复好友关系
    __table_args__ = (
        db.UniqueConstraint('user_id', 'friend_id', name='unique_friendship'),
    )
    
    def __repr__(self):
        return f'<Friendship {self.user_id} <-> {self.friend_id}>'


class DirectMessage(db.Model):
    """私信消息"""
    __tablename__ = 'direct_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 消息内容
    content = db.Column(db.Text, nullable=False)
    
    # 是否已读
    is_read = db.Column(db.Boolean, default=False)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')
    
    def __repr__(self):
        return f'<DirectMessage {self.id}: {self.sender_id} -> {self.receiver_id}>'

'''

    # 在LingStoneRecharge之前插入
    insert_marker = "# ============ 灵石经济系统模型 ============"
    if insert_marker in content:
        content = content.replace(insert_marker, friend_models + "\n" + insert_marker)
    else:
        # 如果找不到标记，就在文件末尾之前添加
        content = content + friend_models
    
    with open('models.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("好友模型添加成功！")

# 添加User模型的friends关系
if 'friends = db.relationship' not in content:
    user_model_section = '''    # 关系
    divinations = db.relationship('Divination', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    lovers = db.relationship('Lover', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    subscriptions = db.relationship('Subscription', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    signins = db.relationship('DailySignin', backref='user', lazy='dynamic', cascade='all, delete-orphan')'''
    
    new_user_model_section = user_model_section + '''
    
    # 便捷好友关系查询（通过Friendship表）
    @property
    def friends_list(self):
        """获取好友列表"""
        friendships = Friendship.query.filter(
            (Friendship.user_id == self.id) | (Friendship.friend_id == self.id)
        ).all()
        friends = []
        for f in friendships:
            if f.user_id == self.id:
                friends.append(f.friend)
            else:
                friends.append(f.user)
        return friends
    
    @property
    def pending_friend_requests(self):
        """获取待处理的好友请求"""
        return FriendRequest.query.filter(
            FriendRequest.receiver_id == self.id,
            FriendRequest.status == 'pending'
        ).all()'''
    
    content = content.replace(user_model_section, new_user_model_section)
    with open('models.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("User模型friends关系添加成功！")
else:
    print("User模型friends关系已存在，跳过")
