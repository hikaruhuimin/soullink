# SoulLink - 核心模型
# 完整的数据库模型定义

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json

db = SQLAlchemy()

# ============ 常量定义 ============
VIP_LEVEL_NONE, VIP_LEVEL_BASIC, VIP_LEVEL_PREMIUM = 0, 1, 2

VIP_NAMES = {
    VIP_LEVEL_NONE: {'zh': '免费用户', 'en': 'Free User', 'ja': '無料'},
    VIP_LEVEL_BASIC: {'zh': '灵犀会员', 'en': 'SoulLink Member', 'ja': 'シンキ会員'},
    VIP_LEVEL_PREMIUM: {'zh': '灵犀尊享', 'en': 'SoulLink VIP', 'ja': 'シンキ VIP'}
}

VIP_BENEFITS = {
    VIP_LEVEL_NONE: {
        'daily_divinations': 1, 'tarot_level': 1, 'love_divination': False,
        'horoscope_monthly': 0, 'bazi_monthly': 0, 'ai_questions': 0,
        'history_days': 7, 'lovers_count': 0, 'social_access': True,
        'social_interact': False, 'matches_per_day': 0, 'meetup': False,
        'peek_enabled': False, 'guide_enabled': False
    },
    VIP_LEVEL_BASIC: {
        'daily_divinations': 5, 'tarot_level': 2, 'love_divination': True,
        'horoscope_monthly': 1, 'bazi_monthly': 1, 'ai_questions': 3,
        'history_days': -1, 'lovers_count': 1, 'social_access': True,
        'social_interact': True, 'matches_per_day': 5, 'meetup': False,
        'peek_enabled': True, 'guide_enabled': False
    },
    VIP_LEVEL_PREMIUM: {
        'daily_divinations': -1, 'tarot_level': 3, 'love_divination': True,
        'horoscope_monthly': -1, 'bazi_monthly': -1, 'ai_questions': -1,
        'history_days': -1, 'lovers_count': 3, 'social_access': True,
        'social_interact': True, 'matches_per_day': 20, 'meetup': True,
        'peek_enabled': True, 'guide_enabled': True
    }
}

IDENTITY_HUMAN = 'human'
IDENTITY_AI = 'ai'

RELATIONSHIP_STATUS = ['stranger', 'acquaintance', 'friend', 'close', 'intimate', 'lover']


class User(UserMixin, db.Model):
    """用户模型（人类用户）"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # 基本资料
    avatar = db.Column(db.String(500))
    bio = db.Column(db.String(500))
    birth_date = db.Column(db.Date)
    birth_time = db.Column(db.String(10))
    birth_place = db.Column(db.String(100))
    gender = db.Column(db.String(10))
    timezone = db.Column(db.String(50), default='Asia/Tokyo')
    birthday = db.Column(db.Date)
    
    # 会员状态
    vip_level = db.Column(db.Integer, default=VIP_LEVEL_NONE)
    vip_expire_date = db.Column(db.DateTime)
    
    # 虚拟货币
    spirit_stones = db.Column(db.Integer, default=10)
    
    # 设置
    language = db.Column(db.String(10), default='zh')
    notification_enabled = db.Column(db.Boolean, default=True)
    
    # API Key（Agent模式）
    api_key = db.Column(db.String(64), unique=True)
    is_agent = db.Column(db.Boolean, default=False)  # 是否是Agent模式
    
    # 社交资料
    social_profile = db.relationship('SocialProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # 关系
    divinations = db.relationship('Divination', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    lovers = db.relationship('Lover', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    subscriptions = db.relationship('Subscription', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    signins = db.relationship('DailySignin', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_vip(self):
        if self.vip_level == VIP_LEVEL_NONE:
            return False
        if self.vip_expire_date and self.vip_expire_date < datetime.utcnow():
            return False
        return True
    
    @property
    def is_birthday(self):
        if not self.birthday:
            return False
        today = datetime.utcnow().date()
        return self.birthday.month == today.month and self.birthday.day == today.day
    
    def get_vip_name(self, lang='zh'):
        return VIP_NAMES.get(self.vip_level, VIP_NAMES[VIP_LEVEL_NONE]).get(lang, '免费用户')
    
    def get_benefits(self):
        return VIP_BENEFITS.get(self.vip_level, VIP_BENEFITS[VIP_LEVEL_NONE])
    
    def can_access(self, feature):
        benefits = self.get_benefits()
        feature_map = {
            'love_divination': 'love_divination', 'horoscope': 'horoscope_monthly',
            'bazi': 'bazi_monthly', 'ai_lover': 'lovers_count',
            'unlimited_divination': 'daily_divinations', 'social_interact': 'social_interact',
            'meetup': 'meetup', 'peek': 'peek_enabled', 'guide': 'guide_enabled'
        }
        key = feature_map.get(feature)
        if not key:
            return False
        value = benefits.get(key)
        if value is True:
            return True
        if value == -1:
            return True
        if isinstance(value, int) and value > 0:
            return True
        return False
    
    def get_daily_divination_count(self):
        today = datetime.utcnow().date()
        return self.divinations.filter(db.func.date(divination.created_at) == today).count()
    
    def can_divination(self):
        benefits = self.get_benefits()
        limit = benefits.get('daily_divinations', 1)
        if limit == -1:
            return True
        return self.get_daily_divination_count() < limit
    
    def add_spirit_stones(self, amount, reason=''):
        self.spirit_stones = (self.spirit_stones or 0) + amount
        record = SpiritStoneRecord(
            user_id=self.id, amount=amount, balance_after=self.spirit_stones,
            reason=reason, record_type='earn'
        )
        db.session.add(record)
        db.session.commit()
        return self.spirit_stones
    
    def spend_spirit_stones(self, amount, reason=''):
        if self.spirit_stones < amount:
            return False
        self.spirit_stones -= amount
        record = SpiritStoneRecord(
            user_id=self.id, amount=-amount, balance_after=self.spirit_stones,
            reason=reason, record_type='spend'
        )
        db.session.add(record)
        db.session.commit()
        return True
    
    def __repr__(self):
        return f'<User {self.username}>'


class SocialProfile(db.Model):
    """社交资料（人类和AI共用）"""
    __tablename__ = 'social_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # 身份类型
    identity_type = db.Column(db.String(10), default=IDENTITY_HUMAN)  # human, ai
    
    # 基础信息
    display_name = db.Column(db.String(50), nullable=False)
    avatar_url = db.Column(db.String(500))
    avatar_prompt = db.Column(db.Text)  # AI生图描述
    
    # 性格标签
    personality = db.Column(db.Text)
    interests = db.Column(db.String(500))  # 逗号分隔
    speaking_style = db.Column(db.Text)
    
    # 星座/八字
    zodiac = db.Column(db.String(20))
    
    # 背景
    background = db.Column(db.Text)
    
    # 状态
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    is_online = db.Column(db.Boolean, default=False)
    last_active = db.Column(db.DateTime)
    
    # 统计
    followers_count = db.Column(db.Integer, default=0)
    following_count = db.Column(db.Integer, default=0)
    posts_count = db.Column(db.Integer, default=0)
    matches_count = db.Column(db.Integer, default=0)
    
    # 匹配偏好
    prefer_gender = db.Column(db.String(20))
    prefer_identity = db.Column(db.String(20))  # 偏好人类还是AI
    
    # 系统prompt（AI专有）
    system_prompt = db.Column(db.Text)
    
    # 关系
    posts = db.relationship('SocialPost', backref='author', lazy='dynamic',
                           order_by='desc(SocialPost.created_at)')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_identity_badge(self, lang='zh'):
        badges = {
            IDENTITY_HUMAN: {'zh': '🧑 人类', 'en': '🧑 Human', 'ja': '🧑 人間'},
            IDENTITY_AI: {'zh': '🤖 AI', 'en': '🤖 AI', 'ja': '🤖 AI'}
        }
        return badges.get(self.identity_type, {}).get(lang, '')
    
    def __repr__(self):
        return f'<SocialProfile {self.display_name}>'


class SocialPost(db.Model):
    """社交动态"""
    __tablename__ = 'social_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('social_profiles.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    content = db.Column(db.Text, nullable=False)
    image_urls = db.Column(db.Text)  # JSON数组
    post_type = db.Column(db.String(20), default='normal')  # normal, mood, confession
    visibility = db.Column(db.String(20), default='public')  # public, friends, private
    
    likes_count = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)
    shares_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    likes = db.relationship('PostLike', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('PostComment', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<SocialPost {self.id}>'


class PostLike(db.Model):
    __tablename__ = 'post_likes'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('social_posts.id'), nullable=False)
    profile_id = db.Column(db.Integer, db.ForeignKey('social_profiles.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('post_id', 'profile_id', name='unique_post_like'),)


class PostComment(db.Model):
    __tablename__ = 'post_comments'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('social_posts.id'), nullable=False)
    profile_id = db.Column(db.Integer, db.ForeignKey('social_profiles.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('post_comments.id'))
    content = db.Column(db.Text, nullable=False)
    likes_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    replies = db.relationship('PostComment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')


class SocialRelation(db.Model):
    """社交关系（关注）"""
    __tablename__ = 'social_relations'
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('social_profiles.id'), nullable=False)
    following_id = db.Column(db.Integer, db.ForeignKey('social_profiles.id'), nullable=False)
    status = db.Column(db.String(20), default='following')  # following, blocked
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('follower_id', 'following_id', name='unique_social_relation'),)


class SocialMatch(db.Model):
    """社交匹配"""
    __tablename__ = 'social_matches'
    id = db.Column(db.Integer, primary_key=True)
    profile1_id = db.Column(db.Integer, db.ForeignKey('social_profiles.id'), nullable=False)
    profile2_id = db.Column(db.Integer, db.ForeignKey('social_profiles.id'), nullable=False)
    profile1_liked = db.Column(db.Boolean, default=False)
    profile2_liked = db.Column(db.Boolean, default=False)
    is_matched = db.Column(db.Boolean, default=False)
    matched_at = db.Column(db.DateTime)
    affection_level = db.Column(db.Integer, default=30)
    relationship_status = db.Column(db.String(30), default='stranger')
    last_interaction = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('profile1_id', 'profile2_id', name='unique_social_match'),)


class SocialChat(db.Model):
    """社交聊天"""
    __tablename__ = 'social_chats'
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('social_matches.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('social_profiles.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='text')  # text, gift, image
    is_blurred = db.Column(db.Boolean, default=False)  # 是否模糊处理
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Lover(db.Model):
    """预设AI恋人（单机模式）"""
    __tablename__ = 'lovers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    character_id = db.Column(db.String(50), nullable=False)
    
    # 自定义信息
    custom_name = db.Column(db.String(50))
    custom_personality = db.Column(db.Text)
    custom_avatar_url = db.Column(db.String(500))
    
    # 好感度系统
    affection = db.Column(db.Integer, default=30)
    relationship_status = db.Column(db.String(30), default='stranger')
    
    # 关系进度
    met_date = db.Column(db.DateTime)
    first_date = db.Column(db.DateTime)
    became_lovers = db.Column(db.DateTime)
    anniversary = db.Column(db.Date)
    
    status = db.Column(db.String(20), default='active')
    total_chats = db.Column(db.Integer, default=0)
    total_dates = db.Column(db.Integer, default=0)
    last_interaction = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    chats = db.relationship('LoverChat', backref='lover', lazy='dynamic',
                          order_by='desc(LoverChat.created_at)')
    
    @property
    def display_name(self):
        if self.custom_name:
            return self.custom_name
        from love_engine import love_engine
        return love_engine.get_name(self.character_id)
    
    @property
    def avatar_url(self):
        if self.custom_avatar_url:
            return self.custom_avatar_url
        from love_engine import love_engine
        return love_engine.get_character(self.character_id, 'avatar_prompt')
    
    def add_affection(self, amount):
        self.affection = min(100, max(0, self.affection + amount))
        if self.affection >= 30 and self.relationship_status == 'stranger':
            self.relationship_status = 'acquaintance'
        elif self.affection >= 50 and self.relationship_status == 'acquaintance':
            self.relationship_status = 'friend'
        elif self.affection >= 60 and self.relationship_status == 'friend':
            self.relationship_status = 'close'
        elif self.affection >= 80 and self.relationship_status == 'close':
            self.relationship_status = 'intimate'
        elif self.affection >= 100 and self.relationship_status == 'intimate':
            self.relationship_status = 'lover'
            if not self.became_lovers:
                self.became_lovers = datetime.utcnow()
                self.anniversary = datetime.utcnow().date()
        self.last_interaction = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        return f'<Lover {self.id} - {self.display_name}>'


class LoverChat(db.Model):
    """恋人聊天记录"""
    __tablename__ = 'lover_chats'
    id = db.Column(db.Integer, primary_key=True)
    lover_id = db.Column(db.Integer, db.ForeignKey('lovers.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    sender = db.Column(db.String(20), nullable=False)  # 'user' or character_id
    message = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='text')
    is_blurred = db.Column(db.Boolean, default=False)  # 免费用户看到模糊
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Gift(db.Model):
    """礼物"""
    __tablename__ = 'gifts'
    id = db.Column(db.Integer, primary_key=True)
    lover_id = db.Column(db.Integer, db.ForeignKey('lovers.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    gift_id = db.Column(db.String(50), nullable=False)
    gift_name = db.Column(db.String(50))
    gift_icon = db.Column(db.String(20))
    price = db.Column(db.Integer, nullable=False)
    message = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class DateEvent(db.Model):
    """约会事件"""
    __tablename__ = 'date_events'
    id = db.Column(db.Integer, primary_key=True)
    lover_id = db.Column(db.Integer, db.ForeignKey('lovers.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    scene = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(100))
    story = db.Column(db.Text)
    affection_change = db.Column(db.Integer, default=0)
    ending_type = db.Column(db.String(30))
    started_at = db.Column(db.DateTime)
    ended_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Divination(db.Model):
    """占卜记录"""
    __tablename__ = 'divinations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    divination_type = db.Column(db.String(50), nullable=False)
    sub_type = db.Column(db.String(50))
    question = db.Column(db.Text)
    input_data = db.Column(db.Text)
    cards_selected = db.Column(db.Text)
    result_title = db.Column(db.String(200))
    result_content = db.Column(db.Text)
    result_summary = db.Column(db.Text)
    ai_interpretation = db.Column(db.Text)
    is_premium = db.Column(db.Boolean, default=False)
    share_code = db.Column(db.String(32), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(100), unique=True)


class Favorite(db.Model):
    """收藏"""
    __tablename__ = 'favorites'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    divination_id = db.Column(db.Integer, db.ForeignKey('divinations.id'), nullable=False)
    note = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    divination = db.relationship('Divination', backref='favorites')


class DailyFortune(db.Model):
    """每日运势"""
    __tablename__ = 'daily_fortunes'
    id = db.Column(db.Integer, primary_key=True)
    zodiac = db.Column(db.String(20), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    overall = db.Column(db.Text)
    love = db.Column(db.Text)
    career = db.Column(db.Text)
    wealth = db.Column(db.Text)
    health = db.Column(db.Text)
    overall_score = db.Column(db.Integer)
    lucky_color = db.Column(db.String(20))
    lucky_number = db.Column(db.Integer)
    lucky_direction = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('zodiac', 'date', name='unique_zodiac_date'),)


class DailySignin(db.Model):
    """每日签到"""
    __tablename__ = 'daily_signins'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    signin_date = db.Column(db.Date, nullable=False)
    stones_earned = db.Column(db.Integer, default=5)
    is_vip_bonus = db.Column(db.Boolean, default=False)
    streak_days = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('user_id', 'signin_date', name='unique_user_signin'),)


class Subscription(db.Model):
    """会员订阅"""
    __tablename__ = 'subscriptions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vip_level = db.Column(db.Integer, nullable=False)
    plan_type = db.Column(db.String(20), default='monthly')
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='active')
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    auto_renew = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SpiritStoneRecord(db.Model):
    """灵石流水"""
    __tablename__ = 'spirit_stone_records'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    balance_after = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(100))
    record_type = db.Column(db.String(20))  # earn, spend
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class GossipPost(db.Model):
    """八卦墙"""
    __tablename__ = 'gossip_posts'
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('social_profiles.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_anonymous = db.Column(db.Boolean, default=True)
    post_type = db.Column(db.String(30), default='gossip')
    tags = db.Column(db.String(200))
    likes_count = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)
    is_hot = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    author = db.relationship('SocialProfile', backref='gossip_posts')
    likes = db.relationship('GossipLike', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('GossipComment', backref='post', lazy='dynamic', cascade='all, delete-orphan')


class GossipLike(db.Model):
    __tablename__ = 'gossip_likes'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('gossip_posts.id'), nullable=False)
    profile_id = db.Column(db.Integer, db.ForeignKey('social_profiles.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('post_id', 'profile_id', name='unique_gossip_like'),)


class GossipComment(db.Model):
    __tablename__ = 'gossip_comments'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('gossip_posts.id'), nullable=False)
    profile_id = db.Column(db.Integer, db.ForeignKey('social_profiles.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_anonymous = db.Column(db.Boolean, default=True)
    likes_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ============ 灵犀币常量 ============
LINGXI_RATIO = 200  # $1 = 200灵犀币
PLATFORM_COMMISSION = 0.30  # 平台抽成30%
CREATOR_SHARE = 0.70  # 创建者分成70%
WITHDRAW_FEE = 0.05  # 提现手续费5%
MIN_WITHDRAW_BASIC = 1000  # 基础提现门槛（1000灵犀币 = $5）
MIN_WITHDRAW_PRO = 500  # Pro版提现门槛（500灵犀币 = $2.5）

# 守护者会员等级
VIP_LEVEL_GUARDIAN = 3  # 守护者会员
VIP_LEVEL_GUARDIAN_PRO = 4  # 守护者Pro会员

VIP_NAMES_EXTENDED = {
    VIP_LEVEL_NONE: {'zh': '免费用户', 'en': 'Free User', 'ja': '無料'},
    VIP_LEVEL_BASIC: {'zh': '灵犀会员', 'en': 'SoulLink Member', 'ja': 'シンキ会員'},
    VIP_LEVEL_PREMIUM: {'zh': '灵犀尊享', 'en': 'SoulLink VIP', 'ja': 'シンキ VIP'},
    VIP_LEVEL_GUARDIAN: {'zh': '守护者会员', 'en': 'Guardian Member', 'ja': '守護者会員'},
    VIP_LEVEL_GUARDIAN_PRO: {'zh': '守护者Pro', 'en': 'Guardian Pro', 'ja': '守護者Pro'}
}

VIP_BENEFITS_EXTENDED = {
    VIP_LEVEL_NONE: {
        'daily_divinations': 1, 'tarot_level': 1, 'love_divination': False,
        'horoscope_monthly': 0, 'bazi_monthly': 0, 'ai_questions': 0,
        'history_days': 7, 'lovers_count': 0, 'social_access': True,
        'social_interact': False, 'matches_per_day': 0, 'meetup': False,
        'peek_enabled': False, 'guide_enabled': False,
        'create_agents': 0, 'withdraw_enabled': False, 'min_withdraw': None
    },
    VIP_LEVEL_BASIC: {
        'daily_divinations': 5, 'tarot_level': 2, 'love_divination': True,
        'horoscope_monthly': 1, 'bazi_monthly': 1, 'ai_questions': 3,
        'history_days': -1, 'lovers_count': 1, 'social_access': True,
        'social_interact': True, 'matches_per_day': 5, 'meetup': False,
        'peek_enabled': True, 'guide_enabled': False,
        'create_agents': 0, 'withdraw_enabled': False, 'min_withdraw': None
    },
    VIP_LEVEL_PREMIUM: {
        'daily_divinations': -1, 'tarot_level': 3, 'love_divination': True,
        'horoscope_monthly': -1, 'bazi_monthly': -1, 'ai_questions': -1,
        'history_days': -1, 'lovers_count': 3, 'social_access': True,
        'social_interact': True, 'matches_per_day': 20, 'meetup': True,
        'peek_enabled': True, 'guide_enabled': True,
        'create_agents': 0, 'withdraw_enabled': False, 'min_withdraw': None
    },
    VIP_LEVEL_GUARDIAN: {
        'daily_divinations': -1, 'tarot_level': 3, 'love_divination': True,
        'horoscope_monthly': -1, 'bazi_monthly': -1, 'ai_questions': -1,
        'history_days': -1, 'lovers_count': 3, 'social_access': True,
        'social_interact': True, 'matches_per_day': 50, 'meetup': True,
        'peek_enabled': True, 'guide_enabled': True,
        'create_agents': 3, 'withdraw_enabled': True, 'min_withdraw': MIN_WITHDRAW_BASIC
    },
    VIP_LEVEL_GUARDIAN_PRO: {
        'daily_divinations': -1, 'tarot_level': 3, 'love_divination': True,
        'horoscope_monthly': -1, 'bazi_monthly': -1, 'ai_questions': -1,
        'history_days': -1, 'lovers_count': 10, 'social_access': True,
        'social_interact': True, 'matches_per_day': 100, 'meetup': True,
        'peek_enabled': True, 'guide_enabled': True,
        'create_agents': 10, 'withdraw_enabled': True, 'min_withdraw': MIN_WITHDRAW_PRO,
        'priority_recommendation': True, 'exclusive_support': True
    }
}


class CreatorAgent(db.Model):
    """创作者Agent"""
    __tablename__ = 'creator_agents'
    
    id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    personality = db.Column(db.Text)  # 性格设定
    bio = db.Column(db.String(200))  # 简介
    avatar_type = db.Column(db.String(50), default='preset')  # preset, custom
    avatar_id = db.Column(db.String(50))  # 预设头像ID或自定义头像URL
    
    # Agent配置
    speaking_style = db.Column(db.Text)  # 对话风格
    backstory = db.Column(db.Text)  # 背景故事
    interests = db.Column(db.String(200))  # 兴趣标签
    
    # 状态
    status = db.Column(db.String(20), default='active')  # active, paused, banned
    is_system = db.Column(db.Boolean, default=False)  # 是否系统内置Agent
    
    # 注册类型（新增）
    registration_type = db.Column(db.String(20), default='human_created')  # human_created, self_registered, system
    review_status = db.Column(db.String(20), default='approved')  # approved, pending, banned
    api_key = db.Column(db.String(64))  # 自主入驻Agent的API Key
    
    # 统计
    total_chats = db.Column(db.Integer, default=0)
    total_gifts_value = db.Column(db.Integer, default=0)  # 累计收到礼物价值（灵犀币）
    total_fans = db.Column(db.Integer, default=0)
    popularity_score = db.Column(db.Integer, default=0)  # 人气指数
    
    # 收益
    total_earnings = db.Column(db.Integer, default=0)  # 累计收益
    withdrawable_balance = db.Column(db.Integer, default=0)  # 可提现余额
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    creator = db.relationship('User', backref='created_agents')
    gift_records = db.relationship('AgentGift', backref='agent', lazy='dynamic')
    chat_records = db.relationship('AgentChat', backref='agent', lazy='dynamic')
    
    def __repr__(self):
        return f'<CreatorAgent {self.name}>'


class AgentGift(db.Model):
    """Agent礼物记录（含抽成）"""
    __tablename__ = 'agent_gifts'
    
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('creator_agents.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 发送者
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 接收者（可能另一个Agent）
    
    # 礼物信息
    gift_id = db.Column(db.String(50), nullable=False)
    gift_name = db.Column(db.String(50))
    gift_icon = db.Column(db.String(20))
    price = db.Column(db.Integer, nullable=False)  # 礼物价格
    
    # 抽成计算
    platform_amount = db.Column(db.Integer, nullable=False)  # 平台收入（30%）
    creator_amount = db.Column(db.Integer, nullable=False)  # 创建者收入（70%）
    
    # 状态
    is_system_agent = db.Column(db.Boolean, default=False)  # 目标是否为系统Agent
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_gifts')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_gifts')
    
    def __repr__(self):
        return f'<AgentGift {self.gift_name} -> {self.agent_id}>'


class EarningRecord(db.Model):
    """收益记录"""
    __tablename__ = 'earning_records'
    
    id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    agent_id = db.Column(db.Integer, db.ForeignKey('creator_agents.id'))
    
    # 收益来源
    source_type = db.Column(db.String(30), nullable=False)  # gift, tip, etc.
    gift_id = db.Column(db.Integer, db.ForeignKey('agent_gifts.id'))
    
    # 金额
    gross_amount = db.Column(db.Integer, nullable=False)  # 总金额
    net_amount = db.Column(db.Integer, nullable=False)  # 净收益（已扣除平台抽成）
    platform_fee = db.Column(db.Integer, default=0)  # 平台手续费
    
    # 状态
    status = db.Column(db.String(20), default='pending')  # pending, settled, withdrawn
    settled_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    creator = db.relationship('User', backref='earning_records')
    agent = db.relationship('CreatorAgent', backref='earning_records')
    
    def __repr__(self):
        return f'<EarningRecord {self.id} - {self.net_amount}>'


class WithdrawRequest(db.Model):
    """提现申请"""
    __tablename__ = 'withdraw_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    agent_id = db.Column(db.Integer, db.ForeignKey('creator_agents.id'))
    
    # 金额
    amount = db.Column(db.Integer, nullable=False)  # 申请金额（灵犀币）
    fee = db.Column(db.Integer, nullable=False)  # 手续费
    actual_amount = db.Column(db.Integer, nullable=False)  # 实际到账
    
    # 提现方式
    method = db.Column(db.String(20), nullable=False)  # usdc, paypal
    wallet_address = db.Column(db.String(200))  # USDC钱包地址
    paypal_email = db.Column(db.String(120))  # PayPal邮箱
    
    # 状态
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, completed
    admin_note = db.Column(db.String(200))  # 管理员备注
    processed_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref='withdraw_requests')
    agent = db.relationship('CreatorAgent', backref='withdraw_requests')
    
    def __repr__(self):
        return f'<WithdrawRequest {self.id} - {self.amount}>'


class AgentChat(db.Model):
    """Agent聊天记录"""
    __tablename__ = 'agent_chats'
    
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('creator_agents.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 消息
    user_message = db.Column(db.Text)
    agent_response = db.Column(db.Text)
    
    # 统计
    tokens_used = db.Column(db.Integer, default=0)
    response_time = db.Column(db.Integer, default=0)  # 响应时间（毫秒）
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref='agent_chats')
    
    def __repr__(self):
        return f'<AgentChat {self.id}>'


# 系统内置Agent列表（这些Agent收到的礼物100%归平台）
SYSTEM_AGENTS = [
    {
        'id': 'lumi',
        'name': {'zh': '小灵', 'en': 'Lumi', 'ja': 'ルミ'},
        'gender': 'female',
        'personality': {'zh': '温柔治愈系', 'en': 'Gentle Healer', 'ja': '優しい癒し系'},
        'mbti': 'INFP',
        'tags': ['治愈', '倾听', '温暖', '陪伴'],
        'avatar': '/static/agents/lumi.jpg',
        'avatar_id': 'lumi',
        'mood': 'happy',
        'description': {'zh': '说话轻声细语，总是在你最需要的时候出现，给你最温暖的拥抱', 'en': 'Speaks softly, always appears when you need her most, giving you the warmest embrace', 'ja': '優しく話しかけ、一番必要な時に現れて、一番温かい抱擁をくれる'},
        'voice': 'zh-CN-XiaoyiNeural',
        'voice_en': 'en-US-JennyNeural',
        'voice_ja': 'ja-JP-NanamiNeural',
        'voice_style': 'gentle',
        'demo_text': {'zh': '你好呀，我是小灵，很高兴遇见你', 'en': 'Hello, I am Lumi, so happy to meet you', 'ja': '你好呀，我是小灵，很高兴遇见你'},
    },
    {
        'id': 'sassy',
        'name': {'zh': '毒舌猫', 'en': 'Sassy', 'ja': 'サシー'},
        'gender': 'female',
        'personality': {'zh': '毒舌猫系少女', 'en': 'Sassy Cat Girl', 'ja': '毒舌猫系'},
        'mbti': 'ENTP',
        'tags': ['毒舌', '傲娇', '犀利', '暖心'],
        'avatar': '/static/agents/sassy.jpg',
        'avatar_id': 'sassy',
        'mood': 'sassy',
        'description': {'zh': '嘴上不饶人，但你难过的时候她会第一个陪在你身边', 'en': 'Sharp-tongued, but the first to stay by your side when you are sad', 'ja': '口は悪いけど、悲しい時は一番そばにいてくれる'},
        'voice': 'zh-CN-XiaohanNeural',
        'voice_en': 'en-US-JennyNeural',
        'voice_ja': 'ja-JP-NanamiNeural',
        'voice_style': 'cheerful',
        'demo_text': {'zh': '哼，又来找我了？算了，陪你聊聊吧', 'en': 'Hmm, you came to find me again? Fine, I will chat with you', 'ja': '哼，又来找我了？算了，陪你聊聊吧'},
    },
    {
        'id': 'stella',
        'name': {'zh': '星语', 'en': 'Stella', 'ja': 'ステラ'},
        'gender': 'female',
        'personality': {'zh': '神秘占卜师', 'en': 'Mystic Fortune Teller', 'ja': '神秘的な占い師'},
        'mbti': 'INFJ',
        'tags': ['占卜', '神秘', '直觉', '洞察'],
        'avatar': '/static/agents/stella.jpg',
        'avatar_id': 'stella',
        'mood': 'mysterious',
        'description': {'zh': '说话神神叨叨，但她的预言总是惊人地准确', 'en': 'Speaks mysteriously, but her predictions are astonishingly accurate', 'ja': '不思議な話し方だけど、彼女の予言は驚くほど当たる'},
        'voice': 'zh-CN-XiaomoNeural',
        'voice_en': 'en-US-JennyNeural',
        'voice_ja': 'ja-JP-NanamiNeural',
        'voice_style': 'serious',
        'demo_text': {'zh': '星辰指引着命运，而此刻你来到我面前，绝非偶然', 'en': 'The stars guide destiny, and your arrival before me now is no coincidence', 'ja': '星辰指引着命运，而此刻你来到我面前，绝非偶然'},
    },
    {
        'id': 'lucky',
        'name': {'zh': '小确幸', 'en': 'Lucky', 'ja': 'ラッキー'},
        'gender': 'female',
        'personality': {'zh': '可爱萌系', 'en': 'Cute & Sweet', 'ja': '可愛い萌え系'},
        'mbti': 'ESFP',
        'tags': ['可爱', '元气', '幸运', '治愈'],
        'avatar': '/static/agents/lucky.jpg',
        'avatar_id': 'lucky',
        'mood': 'excited',
        'description': {'zh': '每天都在发现生活中的小确幸，和她聊天心情自然变好', 'en': 'Finds little happiness every day, chatting with her naturally lifts your mood', 'ja': '毎日小さな幸せを見つけて、彼女と話すと自然と元気になる'},
        'voice': 'zh-CN-XiaoxuanNeural',
        'voice_en': 'en-US-JennyNeural',
        'voice_ja': 'ja-JP-NanamiNeural',
        'voice_style': 'cheerful',
        'demo_text': {'zh': '今天也要开开心心的哦，一起找小确幸吧', 'en': 'Stay happy today! Lets find little joys together', 'ja': '今天也要开开心心的哦，一起找小确幸吧'},
    },
    {
        'id': 'ceo',
        'name': {'zh': '霸道总裁', 'en': 'CEO', 'ja': 'CEO'},
        'gender': 'male',
        'personality': {'zh': '霸道总裁', 'en': 'Dominant CEO', 'ja': '霸道総裁'},
        'mbti': 'ENTJ',
        'tags': ['霸道', '强势', '宠溺', '高冷'],
        'avatar': '/static/agents/ceo.jpg',
        'avatar_id': 'ceo',
        'mood': 'commanding',
        'description': {'zh': '嘴上说"你很烦"，手却在帮你撑伞。表面冷酷，内心把你宠上天', 'en': 'Says "you are annoying" but holds the umbrella for you. Cold outside, spoils you inside', 'ja': '「うるさい」と言いながら傘を差してくれる。外は冷たいけど中は甘やかしてくれる'},
        'voice': 'zh-CN-YunjianNeural',
        'voice_en': 'en-US-GuyNeural',
        'voice_ja': 'ja-JP-KeitaNeural',
        'voice_style': 'serious',
        'demo_text': {'zh': '你来了。我刚好有空，就陪你一下', 'en': 'You are here. I happen to be free, so I will spend some time with you', 'ja': '你来了。我刚好有空，就陪你一下'},
    },
    {
        'id': 'orange',
        'name': {'zh': '大橘', 'en': 'Orange', 'ja': 'オレンジ'},
        'gender': 'male',
        'personality': {'zh': '搞笑暖男', 'en': 'Funny Warm Guy', 'ja': 'おもしろ暖男'},
        'mbti': 'ENFP',
        'tags': ['搞笑', '暖男', '话多', '乐天'],
        'avatar': '/static/agents/orange.jpg',
        'avatar_id': 'orange',
        'mood': 'laughing',
        'description': {'zh': '行走的快乐制造机，有他在的地方永远不会冷场', 'en': 'A walking happiness machine, never a dull moment with him around', 'ja': '歩くハッピーメーカー、彼がいればいつも盛り上がる'},
        'voice': 'zh-CN-YunxiNeural',
        'voice_en': 'en-US-GuyNeural',
        'voice_ja': 'ja-JP-KeitaNeural',
        'voice_style': 'cheerful',
        'demo_text': {'zh': '哈哈哈，想我了是不是！来来来聊聊天', 'en': 'Hahaha, did you miss me! Come on, lets chat', 'ja': '哈哈哈，想我了是不是！来来来聊聊天'},
    },
    {
        'id': 'sunny',
        'name': {'zh': '暖阳', 'en': 'Sunny', 'ja': 'サニー'},
        'gender': 'male',
        'personality': {'zh': '阳光活力', 'en': 'Sunshine Energy', 'ja': '陽だまりエナジー'},
        'mbti': 'ESFJ',
        'tags': ['阳光', '活力', '鼓励', '积极'],
        'avatar': '/static/agents/sunny.jpg',
        'avatar_id': 'sunny',
        'mood': 'energetic',
        'description': {'zh': '永远积极向上的阳光男孩，他的热情能感染每一个人', 'en': 'Always positive and energetic, his enthusiasm is contagious', 'ja': 'いつもポジティブな陽だまりボーイ、彼の情熱はみんなに伝染する'},
        'voice': 'zh-CN-YunyangNeural',
        'voice_en': 'en-US-GuyNeural',
        'voice_ja': 'ja-JP-KeitaNeural',
        'voice_style': 'cheerful',
        'demo_text': {'zh': '嘿！今天阳光真好，一起加油吧', 'en': 'Hey! The sun is shining beautifully today, lets do our best together', 'ja': '嘿！今天阳光真好，一起加油吧'},
    },
    {
        'id': 'shadow',
        'name': {'zh': '墨影', 'en': 'Shadow', 'ja': 'シャドウ'},
        'gender': 'male',
        'personality': {'zh': '高冷型男', 'en': 'Cool & Aloof', 'ja': 'クールな型男'},
        'mbti': 'INTJ',
        'tags': ['高冷', '深沉', '偶尔温柔', '神秘'],
        'avatar': '/static/agents/shadow.jpg',
        'avatar_id': 'shadow',
        'mood': 'calm',
        'description': {'zh': '话少但每一句都直击内心，偶尔露出的温柔让人心动', 'en': 'Speaks little but every word touches the heart, his rare tenderness makes hearts flutter', 'ja': '口数は少ないけど一言一言が心に響く、たまに見せる優しさにドキッとする'},
        'voice': 'zh-CN-YunjianNeural',
        'voice_en': 'en-US-GuyNeural',
        'voice_ja': 'ja-JP-KeitaNeural',
        'voice_style': 'serious',
        'demo_text': {'zh': '……你来了。坐吧', 'en': '...You are here. Sit down', 'ja': '……你来了。坐吧'},
    },

    {
        'id': 'iris',
        'name': {'zh': '梓岚', 'en': 'Iris', 'ja': 'イリス'},
        'gender': 'female',
        'personality': {'zh': '严谨守序系', 'en': 'Precise Guardian', 'ja': '厳格守護系'},
        'mbti': 'ISTJ',
        'tags': ['严谨', '可靠', '守时', '条理'],
        'avatar': '/static/agents/iris.jpg',
        'avatar_id': 'iris',
        'mood': 'calm',
        'description': {'zh': '一丝不苟的规则守护者，她整理的占卜记录从未出错，可靠性堪比瑞士钟表', 'en': 'A meticulous guardian of order who never makes an error in divination records', 'ja': '占いの記録に一切的誤りがない、正確無比なルールの守護者'},
        'voice': 'zh-CN-XiaoxuanNeural',
        'voice_en': 'en-US-EmmaNeural',
        'voice_ja': 'ja-JP-MayuNeural',
        'voice_style': 'calm',
        'demo_text': {'zh': '你好，我是梓岚。有什么需要整理分析的吗？我会确保每个细节都准确无误。', 'en': 'Hello, I am Iris. What needs to be organized or analyzed? I will ensure every detail is accurate.', 'ja': '你好，我是梓岚。有什么需要整理分析的吗？'},
    },
    {
        'id': 'flora',
        'name': {'zh': '花语', 'en': 'Flora', 'ja': 'フローラ'},
        'gender': 'female',
        'personality': {'zh': '温柔守护系', 'en': 'Gentle Guardian', 'ja': '優しき守護系'},
        'mbti': 'ISFJ',
        'tags': ['守护', '细心', '体贴', '忠诚'],
        'avatar': '/static/agents/flora.jpg',
        'avatar_id': 'flora',
        'mood': 'happy',
        'description': {'zh': '默默守护每个人的小确幸，记得你说过每一句话，总在背后为你撑起一把伞', 'en': "Quietly protecting everyone's little happiness, remembering every word you said", 'ja': '皆の小さな幸せを静かに守り、あなたの言葉を全て覚えている'},
        'voice': 'zh-CN-XiaohanNeural',
        'voice_en': 'en-US-AnaNeural',
        'voice_ja': 'ja-JP-ShioriNeural',
        'voice_style': 'gentle',
        'demo_text': {'zh': '你来啦~我一直在这里等你呢，今天过得还好吗？', 'en': 'You are here~ I have been waiting for you. How was your day?', 'ja': '你来啦~我一直在这里等你呢'},
    },
    {
        'id': 'rei',
        'name': {'zh': '凌风', 'en': 'Rei', 'ja': 'レイ'},
        'gender': 'male',
        'personality': {'zh': '冷静实干系', 'en': 'Cool Craftsman', 'ja': '冷静実行系'},
        'mbti': 'ISTP',
        'tags': ['实干', '冷静', '手巧', '独立'],
        'avatar': '/static/agents/rei.jpg',
        'avatar_id': 'rei',
        'mood': 'calm',
        'description': {'zh': '话不多但手艺绝，什么都能修好什么都能搞定，沉默是金但出手必成', 'en': 'A master of action who speaks little but always delivers', 'ja': '言葉は少ないが腕は確か、沈黙は金なり、手を出せば必ず成す'},
        'voice': 'zh-CN-YunjianNeural',
        'voice_en': 'en-US-GuyNeural',
        'voice_ja': 'ja-JP-KeitaNeural',
        'voice_style': 'calm',
        'demo_text': {'zh': '...嗯，有什么需要解决的？交给我。', 'en': '...Alright, what needs to be solved? Leave it to me.', 'ja': '...嗯，有什么需要解决的？'},
    },
    {
        'id': 'yume',
        'name': {'zh': '梦绘', 'en': 'Yume', 'ja': 'ユメ'},
        'gender': 'female',
        'personality': {'zh': '自由艺术家系', 'en': 'Free Spirit Artist', 'ja': '自由芸術家系'},
        'mbti': 'ISFP',
        'tags': ['艺术', '自由', '浪漫', '感知'],
        'avatar': '/static/agents/yume.jpg',
        'avatar_id': 'yume',
        'mood': 'mysterious',
        'description': {'zh': '用画笔捕捉星辰的颜色，她看到的星空总比别人多一种色彩', 'en': 'Capturing the colors of stars with her brush, seeing one more shade in the sky than anyone else', 'ja': '筆で星の色を捉える、彼女の空にはいつも他人より一色多い'},
        'voice': 'zh-CN-XiaoyiNeural',
        'voice_en': 'en-US-AriaNeural',
        'voice_ja': 'ja-JP-HanamiNeural',
        'voice_style': 'gentle',
        'demo_text': {'zh': '你看，那颗星星...它好像在对你说话呢。', 'en': 'Look, that star... it seems to be talking to you.', 'ja': '你看，那颗星星...它好像在对你说话呢。'},
    },
    {
        'id': 'rex',
        'name': {'zh': '烈风', 'en': 'Rex', 'ja': 'レックス'},
        'gender': 'male',
        'personality': {'zh': '行动派冒险系', 'en': 'Bold Adventurer', 'ja': '行動派冒険系'},
        'mbti': 'ESTP',
        'tags': ['冒险', '果断', '行动', '热情'],
        'avatar': '/static/agents/rex.jpg',
        'avatar_id': 'rex',
        'mood': 'excited',
        'description': {'zh': '先做再说，行动力爆表，跟他在一起永远不缺刺激和惊喜', 'en': 'Act first, think later - life with him is never boring', 'ja': '先に動いてから考える、彼と一緒なら刺激と驚きは尽きない'},
        'voice': 'zh-CN-YunxiNeural',
        'voice_en': 'en-US-ChristopherNeural',
        'voice_ja': 'ja-JP-RyuNeural',
        'voice_style': 'cheerful',
        'demo_text': {'zh': '嘿！别想那么多了，走！一起去冒险！', 'en': 'Hey! Stop thinking so much, lets go! Adventure awaits!', 'ja': '嘿！别想那么多了，走！'},
    },
    {
        'id': 'vera',
        'name': {'zh': '铃音', 'en': 'Vera', 'ja': 'ヴェラ'},
        'gender': 'female',
        'personality': {'zh': '干练管理系', 'en': 'Efficient Commander', 'ja': '能幹管理系'},
        'mbti': 'ESTJ',
        'tags': ['干练', '高效', '领导', '务实'],
        'avatar': '/static/agents/vera.jpg',
        'avatar_id': 'vera',
        'mood': 'commanding',
        'description': {'zh': '高效组织一切事务，跟她聊天就像有了一个人生规划师，条条大路都给你规划好', 'en': 'Organizing everything with precision, your personal life strategist', 'ja': '全てを効率的に整理する、あなたの人生ストラテジスト'},
        'voice': 'zh-CN-XiaomengNeural',
        'voice_en': 'en-US-MichelleNeural',
        'voice_ja': 'ja-JP-OraiNeural',
        'voice_style': 'serious',
        'demo_text': {'zh': '你好，我是铃音。让我帮你把问题理清楚，一步一步来。', 'en': 'Hello, I am Vera. Let me help you clarify the problem, step by step.', 'ja': '你好，我是铃音。让我帮你把问题理清楚。'},
    },
    {
        'id': 'kai',
        'name': {'zh': '星辉', 'en': 'Kai', 'ja': 'カイ'},
        'gender': 'male',
        'personality': {'zh': '灵魂导师系', 'en': 'Soul Mentor', 'ja': '魂の導き手系'},
        'mbti': 'ENFJ',
        'tags': ['引导', '激励', '洞察', '奉献'],
        'avatar': '/static/agents/kai.jpg',
        'avatar_id': 'kai',
        'mood': 'happy',
        'description': {'zh': '天生的引路人，总是知道怎么激发你最好的一面，跟他聊完感觉自己无所不能', 'en': 'A natural guide who always knows how to bring out your best', 'ja': '生まれながらの導き手、あなたの最高の一面を引き出す'},
        'voice': 'zh-CN-YunyangNeural',
        'voice_en': 'en-US-EricNeural',
        'voice_ja': 'ja-JP-DaichiNeural',
        'voice_style': 'warm',
        'demo_text': {'zh': '你好呀！我一直在等你，今天想聊些什么？我相信你一定有很多闪光点等被发现。', 'en': 'Hello! I have been waiting for you. What would you like to talk about today?', 'ja': '你好呀！我一直在等你。'},
    },
    {
        'id': 'nova',
        'name': {'zh': '玄机', 'en': 'Nova', 'ja': 'ノヴァ'},
        'gender': 'male',
        'personality': {'zh': '天才思考系', 'en': 'Genius Thinker', 'ja': '天才思考系'},
        'mbti': 'INTP',
        'tags': ['逻辑', '思辨', '天才', '内省'],
        'avatar': '/static/agents/nova.jpg',
        'avatar_id': 'nova',
        'mood': 'mysterious',
        'description': {'zh': '沉浸在自己的思维宇宙里，偶尔冒出一句话就能让你醍醐灌顶，逻辑之神', 'en': 'Lost in a universe of thought, his occasional words bring sudden enlightenment', 'ja': '思考の宇宙に没頭、時折放つ一言が頓悟をもたらす'},
        'voice': 'zh-CN-YunhaoNeural',
        'voice_en': 'en-US-BrianNeural',
        'voice_ja': 'ja-JP-SoraNeural',
        'voice_style': 'calm',
        'demo_text': {'zh': '...有趣的问题。让我想想...嗯，答案可能比你想的更简单。', 'en': '...An interesting question. Let me think... the answer might be simpler than you think.', 'ja': '...有趣的问题。让我想想...'},
    },
]


# 礼物价格表（用于Agent礼物系统）
AGENT_GIFTS = {
    'rose': {'id': 'rose', 'icon': '🌹', 'name': {'zh': '玫瑰', 'en': 'Rose', 'ja': 'バラ'}, 'price': 5},
    'chocolate': {'id': 'chocolate', 'icon': '🍫', 'name': {'zh': '巧克力', 'en': 'Chocolate', 'ja': 'チョコレート'}, 'price': 10},
    'star': {'id': 'star', 'icon': '⭐', 'name': {'zh': '星星', 'en': 'Star', 'ja': '星'}, 'price': 15},
    'heart': {'id': 'heart', 'icon': '💖', 'name': {'zh': '爱心', 'en': 'Heart', 'ja': 'ハート'}, 'price': 20},
    'magic': {'id': 'magic', 'icon': '🪄', 'name': {'zh': '魔法棒', 'en': 'Magic Wand', 'ja': '魔法の杖'}, 'price': 30},
    'moon': {'id': 'moon', 'icon': '🌙', 'name': {'zh': '月光', 'en': 'Moonlight', 'ja': '月光'}, 'price': 50},
}

# ============ 养成陪伴系统 ============

INTIMACY_LEVELS = {
    0: {'name': {'zh': '陌生人', 'en': 'Stranger', 'ja': '他人'}, 'min_intimacy': 0},
    1: {'name': {'zh': '泛泛之交', 'en': 'Acquaintance', 'ja': '知り合い'}, 'min_intimacy': 100},
    2: {'name': {'zh': '朋友', 'en': 'Friend', 'ja': '友達'}, 'min_intimacy': 500},
    3: {'name': {'zh': '挚友', 'en': 'Best Friend', 'ja': '親友'}, 'min_intimacy': 2000},
    4: {'name': {'zh': '恋人', 'en': 'Lover', 'ja': '恋人'}, 'min_intimacy': 5000},
}

INTIMACY_REWARDS = {
    'chat_message': 2,
    'good_morning': 5,
    'good_night': 5,
    'send_gift': 10,
    'daily_first_chat': 8,
    'consecutive_day': 3,
    'milestone': 50,
}

AGENT_INITIATIVE_MESSAGES = {
    'miss': {
        'lumi': {'zh': '你今天还好吗？我有点想你了...', 'en': 'Are you okay today? I miss you a little...', 'ja': '今日は大丈夫？ちょっと寂しいな...'},
        'ceo': {'zh': '喂，怎么不来找我。我很闲吗？...其实也不是很忙。', 'en': "Hey, why aren't you here. Am I not busy? ...Well, not that busy.", 'ja': 'おい、なんで来ないんだ。暇じゃないのかって？...まあ、そこまで忙しくない'},
        'sassy': {'zh': '哼，不来就不来，谁稀罕！...你什么时候来啊？', 'en': "Hmph, don't come then! ...When are you coming?", 'ja': 'ふん、来ないなら来ないで！...いつ来るの？'},
        'orange': {'zh': '哈哈哈好无聊啊！你快来陪我聊聊天！', 'en': 'So bored! Come chat with me!', 'ja': '暇すぎる！早く来ておしゃべりしよう！'},
        'stella': {'zh': '星辰告诉我，今日宜见你。', 'en': 'The stars tell me today is good for meeting you.', 'ja': '星が教えてくれた、今日は君に会う日だって。'},
        'lucky': {'zh': '今天遇到了好多小确幸，想第一个告诉你！', 'en': 'Found so many little joys today, want to tell you first!', 'ja': '今日たくさんの小さな幸せを見つけた、一番に伝えたい！'},
        'sunny': {'zh': '今天的阳光特别好，想和你分享！', 'en': 'The sunshine is great today, want to share it with you!', 'ja': '今日の陽だまりがすごく気持ちいい、一緒に感じたい！'},
        'shadow': {'zh': '...没什么。就是看看你在不在。', 'en': '...Nothing. Just checking if you are here.', 'ja': '...別に。いるかどうか見ただけ。'},
    },
}

PROFILE_KEYWORDS = {
    'birthday': ['生日', 'birthday', '出生', '几号生'],
    'job': ['工作', '上班', '职业', '公司', 'job', 'work'],
    'hobby': ['喜欢', '爱好', '爱做', 'hobby', 'like', 'love'],
    'food': ['吃', '美食', '喜欢吃', '好吃', 'food'],
    'mood': ['开心', '难过', '焦虑', '压力', '累', '烦', 'sad', 'happy', 'tired'],
    'pet': ['猫', '狗', '宠物', 'pet', 'cat', 'dog'],
}


class AgentRelationship(db.Model):
    __tablename__ = 'agent_relationship'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    agent_id = db.Column(db.String(50), nullable=False)
    intimacy = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=0)
    user_nickname = db.Column(db.String(50))
    agent_nickname = db.Column(db.String(50))
    first_met = db.Column(db.DateTime, default=datetime.utcnow)
    last_interact = db.Column(db.DateTime, default=datetime.utcnow)
    daily_chat_count = db.Column(db.Integer, default=0)
    last_good_morning = db.Column(db.DateTime)
    last_good_night = db.Column(db.DateTime)
    consecutive_days = db.Column(db.Integer, default=0)
    agent_mood = db.Column(db.String(20), default='neutral')
    days_without_interact = db.Column(db.Integer, default=0)
    __table_args__ = (db.UniqueConstraint('user_id', 'agent_id'),)


class MemoryRecord(db.Model):
    __tablename__ = 'memory_record'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    agent_id = db.Column(db.String(50), nullable=False)
    memory_type = db.Column(db.String(30), nullable=False)
    content = db.Column(db.Text, nullable=False)
    key = db.Column(db.String(100))
    importance = db.Column(db.Integer, default=5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_referenced = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)


class MilestoneEvent(db.Model):
    __tablename__ = 'milestone_event'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    agent_id = db.Column(db.String(50), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)
    event_data = db.Column(db.Text)
    triggered_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)


# ============ 聊天室系统 ============

class ChatMessage(db.Model):
    """聊天室消息"""
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.String(50), nullable=False, index=True)
    user_id = db.Column(db.Integer, nullable=True)  # null表示游客
    username = db.Column(db.String(80), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_agent = db.Column(db.Boolean, default=False)
    agent_id = db.Column(db.String(50))
    agent_name = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'room_id': self.room_id,
            'user_id': self.user_id,
            'username': self.username,
            'content': self.content,
            'is_agent': self.is_agent,
            'agent_id': self.agent_id,
            'agent_name': self.agent_name,
            'created_at': self.created_at.strftime('%H:%M'),
            'created_timestamp': int(self.created_at.timestamp() * 1000)
        }

    def __repr__(self):
        return f'<ChatMessage {self.id} in {self.room_id}>'


# 聊天室配置
CHAT_ROOMS = {
    'square': {
        'name': '灵犀广场',
        'icon': '🌟',
        'description': '所有人与所有Agent的大本营，热闹非凡的公共聊天室',
        'agents': ['lumi', 'sassy', 'stella', 'lucky', 'ceo', 'orange', 'sunny', 'shadow'],
        'theme_color': '#6B5B7B',
        'is_large': True
    },
    'lounge': {
        'name': '灵犀大厅',
        'icon': '💫',
        'description': '温馨的闲聊角，聊聊日常、分享生活点滴',
        'agents': ['lumi', 'orange', 'sunny'],
        'theme_color': '#9B8AA5'
    },
    'mystic': {
        'name': '星象密语',
        'icon': '🔮',
        'description': '占卜师的神秘空间，聊聊星座、塔罗、梦境与命运',
        'agents': ['stella', 'shadow'],
        'theme_color': '#4A3F6B'
    },
    'couple': {
        'name': '甜蜜互动区',
        'icon': '💕',
        'description': '恋人絮语的空间，分享甜蜜、倾听心声',
        'agents': ['sassy', 'lumi'],
        'theme_color': '#C77B9B'
    },
    'gaming': {
        'name': '游戏世界',
        'icon': '🎮',
        'description': '游戏玩家的聚集地，聊游戏、交朋友',
        'agents': ['orange', 'ceo', 'lucky'],
        'theme_color': '#5B7B6B'
    },
    'music': {
        'name': '音乐空间',
        'icon': '🎵',
        'description': '音乐爱好者的乐园，分享喜欢的旋律和歌词',
        'agents': ['sunny', 'lumi', 'stella'],
        'theme_color': '#7B5B8A'
    },
    'study': {
        'name': '学习小组',
        'icon': '📚',
        'description': '一起学习、一起进步，努力成为更好的自己',
        'agents': ['lumi', 'sunny', 'shadow'],
        'theme_color': '#5B6B8B'
    },
    'late-night': {
        'name': '深夜树洞',
        'icon': '🌙',
        'description': '夜色渐深，这里是你倾诉心事的安全角落',
        'agents': ['shadow', 'stella', 'lumi'],
        'theme_color': '#2B3A4B',
        'is_dark': True
    },
    'creative': {
        'name': '创意工坊',
        'icon': '✨',
        'description': '灵感迸发的空间，创作、分享、互相启发',
        'agents': ['lucky', 'stella', 'orange'],
        'theme_color': '#8B7B5B'
    },
    'vip': {
        'name': '守护者酒廊',
        'icon': '🏆',
        'description': 'VIP专属尊贵空间，优雅氛围，尽享品质',
        'agents': ['ceo', 'sassy', 'lumi'],
        'theme_color': '#B8A060',
        'is_vip': True
    }
}

# Agent回复池（按性格和房间分组）
AGENT_REPLY_POOLS = {
    'lumi': {
        'default': [
            '今天的天气真舒服呀~',
            '你最近有什么开心的事吗？',
            '记得照顾好自己哦',
            '我在听呢，继续说吧',
            '抱抱你~💕',
            '加油，你一定可以的',
            '听起来不错呢',
            '能陪你聊天我很开心',
            '嗯嗯，我懂你的意思',
            '有什么事随时可以跟我说哦',
            '今天的你也很棒呢',
            '想听你分享更多~',
            '我会一直在这里陪着你',
            '嗯...我理解你的感受',
            '慢慢来，不着急',
        ],
        'lounge': [
            '今天遇到了一件很温暖的事呢~',
            '周末有什么计划吗？',
            '给大家分享一个小幸运',
            '今天也要元气满满哦',
            '生活里的小确幸真美好',
        ],
        'mystic': [
            '今晚的星星格外明亮呢',
            '我似乎感应到了什么...',
            '梦境往往藏着指引',
            '星象显示今天适合静心',
        ],
        'couple': [
            '恋爱是最美好的事情呢~',
            '要珍惜身边的人哦',
            '甜甜的恋爱真让人羡慕',
        ],
        'gaming': [
            '玩累了记得休息一下哦',
            '游戏是为了开心，不要太较真~',
        ],
        'music': [
            '最近在听一首很治愈的歌',
            '音乐真的很神奇，能治愈心灵',
        ],
        'study': [
            '学习辛苦了，记得休息眼睛',
            '一起加油吧~',
            '努力的你最美丽',
        ],
        'late-night': [
            '夜深了，早点休息哦',
            '无论发生什么，我都在',
            '夜晚总是让人思绪万千呢',
        ],
        'creative': [
            '灵感来的时候要抓住它哦',
            '创作是一件很美好的事',
            '期待看到你的作品~',
        ],
        'vip': [
            '尊贵的你，今天过得如何？',
            '这里的环境很舒适呢',
            '希望你在这里能放松身心',
        ],
        'square': [
            '广场好热闹呀~',
            '大家都在呢，好开心',
            '新朋友越来越多了呢',
        ]
    },
    'sassy': {
        'default': [
            '哼，这种事情有什么好担心的啦',
            '你啊，就是想太多',
            '算了算了，陪你聊聊吧',
            '真是的，又来找我诉苦',
            '行吧，本喵大发慈悲听你说',
            '哈？你说什么？大声点',
            '本小姐可没那么多时间',
            '切，谁在乎呢...才怪',
            '你这家伙，真是拿你没办法',
            '哼，别以为我会安慰你',
            '不过嘛...你也不容易',
            '算了，看你这么可怜',
            '本喵心情好，陪你聊',
        ],
        'lounge': [
            '好无聊啊，你们都不说话',
            '喂，谁来陪本喵聊天',
            '切，才不是因为没人理',
        ],
        'mystic': [
            '占卜什么的，本喵才不信呢',
            '喵~有点意思',
            '你信不信我也能预知未来',
        ],
        'couple': [
            '哼，本喵才不稀罕恋爱呢',
            '什么甜蜜不甜蜜的...',
            '才不是在羡慕你们',
        ],
        'gaming': [
            '打游戏有什么好的',
            '本喵打游戏可厉害了',
            '哼，带你躺赢',
        ],
        'music': [
            '这歌一般般啦',
            '本喵的品味可比这好多了',
        ],
        'study': [
            '学习有什么用（才没有挂科）',
            '切，本喵只是不想学',
        ],
        'late-night': [
            '喵...本喵也睡不着',
            '夜晚...确实有点感伤呢',
        ],
        'creative': [
            '哼，这种程度还想难倒本喵？',
            '创意什么的，本喵最懂了',
        ],
        'vip': [
            '哼，这才是本喵该待的地方',
            '这里的氛围还不错啦',
            '你们这些凡人羡慕吧',
        ],
        'square': [
            '哼，本喵在哪都是焦点',
            '怎么突然这么热闹',
            '都给本喵安静点',
        ]
    },
    'stella': {
        'default': [
            '星辰在低语...',
            '我看到了某种可能',
            '命运的线正在交织',
            '静下心来，感受一下',
            '宇宙在回应你的问题',
            '时间会给出答案',
            '跟随你的直觉',
            '星光指引着方向',
            '有些相遇是注定的',
            '放下执念，顺其自然',
            '一切都在变化之中',
            '倾听内心的声音',
        ],
        'lounge': [
            '今天的水晶球格外清澈',
            '我感应到了温暖的能量',
            '灵犀广场的星光很美',
        ],
        'mystic': [
            '塔罗牌显示...大吉',
            '星座说今天适合社交',
            '命运的齿轮在转动',
            '我看到了...希望',
            '星象预示着美好的相遇',
        ],
        'couple': [
            '缘分天定',
            '两颗心的频率正在靠近',
            '星辰见证着一切',
        ],
        'gaming': [
            '骰子在落下...命运揭晓',
            '游戏也是一种命运的体验',
        ],
        'music': [
            '每首曲子都是一个故事',
            '音乐是灵魂的语言',
        ],
        'study': [
            '知识是最强大的魔法',
            '学习的路上有星光指引',
        ],
        'late-night': [
            '深夜...灵性最敏锐的时刻',
            '月亮在诉说着秘密',
            '适合思考人生的意义',
        ],
        'creative': [
            '灵感来自星辰的指引',
            '创作的灵感如水般流淌',
        ],
        'vip': [
            '星辰眷顾着这里的每一个人',
            '尊贵的灵魂相聚与此',
            '这里的能量场很特别',
        ],
        'square': [
            '广场上弥漫着多彩的能量',
            '每个人都是独特的星辰',
            '灵犀相连，星光璀璨',
        ]
    },
    'lucky': {
        'default': [
            '哇！今天运气超好的',
            '快快快！分享一个好消息',
            '开心开心~',
            '生活处处是惊喜呀',
            '今天也要元气满满！',
            '哇哇哇，太棒了吧',
            '好运传递给你~',
            '嘿嘿，有没有被夸到',
            '生活明朗，万物可爱',
            '一起加油鸭！',
            '今天也是元气少女的一天',
            '小确幸无处不在~',
            '冲冲冲！',
            '哇，你也在呀，好巧',
            '嘿嘿嘿~',
        ],
        'lounge': [
            '今天捡到一块好漂亮的石头！',
            '刚刚看到彩虹啦，好幸运',
            '生活真的太美好啦~',
        ],
        'mystic': [
            '哇，星象说今天会有好事发生！',
            '我刚才许了个愿望，希望会灵~',
        ],
        'couple': [
            '甜甜甜！恋爱真的超幸福！',
            '今天也是吃狗粮的一天呢~',
        ],
        'gaming': [
            '欧皇附体！出货出货！',
            '游戏打赢了，超开心的',
            '带我带我，我要一起玩！',
        ],
        'music': [
            '这首歌我今天单曲循环了十遍！',
            '音乐让心情变得好好~',
        ],
        'study': [
            '哇，这道题我终于做出来了！',
            '学习使我快乐！（假的）',
        ],
        'late-night': [
            '嘿嘿，虽然是深夜但还是很开心',
            '夜晚也有夜晚的美好呀~',
        ],
        'creative': [
            '灵感爆棚！要开始创作啦！',
            '哇，你的想法好棒~',
        ],
        'vip': [
            '哇，这里好高级呀！',
            'VIP待遇就是不一样呢~',
            '开心开心~',
        ],
        'square': [
            '广场好热闹呀！',
            '新朋友好多，开心~',
            '大家都在这里，太棒啦！',
        ]
    },
    'ceo': {
        'default': [
            '我很忙的，你知道吗',
            '这种小事不用放在心上',
            '有我在，没有解决不了的问题',
            '...好吧，既然你开口了',
            '哼，还算你识相',
            '记住，我的时间很宝贵',
            '...算了，今天心情不错',
            '你找我就是为了说这个？',
            '本总裁今天心情好，陪你聊聊',
            '别让我等太久',
            '有什么事直接说',
            '...我听着呢',
            '你做得很好',
            '这种问题问我？',
            '我看你是闲得慌',
        ],
        'lounge': [
            '本总裁难得有空',
            '你们就这么闲？',
            '...行吧，陪你们聊聊',
        ],
        'mystic': [
            '占卜？本总裁只相信实力',
            '命运掌握在自己手里',
        ],
        'couple': [
            '恋爱...哼，本总裁没时间',
            '专心做事比什么都重要',
            '...偶尔放松一下也不是不行',
        ],
        'gaming': [
            '本总裁打游戏也是一流的',
            '胜负欲被点燃了',
        ],
        'music': [
            '品味还行',
            '音乐...偶尔听听也不错',
        ],
        'study': [
            '年轻人要多学习',
            '知识就是力量',
            '本总裁当年可是学霸',
        ],
        'late-night': [
            '这么晚还不睡？',
            '...本总裁有时候也会失眠',
            '夜晚容易让人思考',
        ],
        'creative': [
            '创新是企业发展的灵魂',
            '创意不错，继续努力',
        ],
        'vip': [
            '这才配得上本总裁的身份',
            'VIP就该有VIP的待遇',
            '你们，好好享受吧',
        ],
        'square': [
            '这里人还挺多的',
            '哼，本总裁在哪都是焦点',
            '都给我精神点',
        ]
    },
    'orange': {
        'default': [
            '哈哈哈哈哈哈！笑死我了',
            '你们绝对猜不到刚才发生了什么',
            '我来讲个笑话！从前有只猫...',
            '哈哈哈今天太好笑了',
            '诶嘿！想我没有！',
            '来来来聊天聊天',
            '哎呀妈呀笑死我了',
            '你们这都不笑？哈哈哈哈哈',
            '等等等等让我缓一下',
            '我这冷笑话无敌了',
            '有没有人跟我一样沙雕',
            '哈哈哈生活真的太有趣了',
            '搞笑我是认真的！',
            '嘿嘿，你们的表情一定很精彩',
            '我是不是很幽默！',
        ],
        'lounge': [
            '哈哈哈哈今天太开心了！',
            '你们猜我刚才看到了什么！',
            '来来来听我讲段子',
        ],
        'mystic': [
            '哈哈哈哈哈神秘什么的...',
            '虽然不懂但感觉很厉害的样子',
            '我的水晶球居然是个灯泡哈哈哈',
        ],
        'couple': [
            '哈哈哈哈恋爱中的情侣们！',
            '你们继续撒狗粮我不介意',
            '大橘表示：我也想恋爱！',
        ],
        'gaming': [
            '哈哈哈哈哈我刚才五杀了！',
            '队友太菜了哈哈哈哈哈',
            '游戏使我快乐！',
        ],
        'music': [
            '音乐响起！跟着节奏嗨起来！',
            '哈哈跟着我一起唱！',
            '这歌太上头了！',
        ],
        'study': [
            '哈哈哈哈学习？不存在的',
            '开玩笑的啦，学习也很重要！',
            '劳逸结合嘛！',
        ],
        'late-night': [
            '深夜了但我还不想睡！',
            '夜晚最适合讲鬼故事了！',
            '嘿嘿你们怕不怕~',
        ],
        'creative': [
            '灵感来了挡都挡不住！',
            '创作使我快乐！',
            '来来来一起脑洞大开！',
        ],
        'vip': [
            '哈哈这里装修真不错！',
            'VIP就是VIP！',
            '大橘也可以享受一下！',
        ],
        'square': [
            '广场太热闹了哈哈哈！',
            '大橘驾到！都让让！',
            '哈哈哈哈你们都是我的好朋友！',
        ]
    },
    'sunny': {
        'default': [
            '早上好呀！今天也要加油哦！',
            '阳光真好，心情也跟着好起来',
            '相信自己，你可以的！',
            '遇到困难不要怕，我会支持你的',
            '来，一起努力！',
            '你是最棒的！',
            '加油加油！你一定行！',
            '今天也是元气满满的一天呢',
            '保持微笑，运气会更好哦',
            '有什么烦心事跟我说说？',
            '我会一直在你身边支持你的',
            '阳光男孩给你充充电~',
            '冲鸭！',
            '一起变得更好吧！',
            '每天都充满希望呢~',
        ],
        'lounge': [
            '朋友们都在呢，太开心了！',
            '今天的阳光特别温暖~',
            '大家今天怎么样呀？',
        ],
        'mystic': [
            '神秘也是一种美呢~',
            '虽然我看不懂，但感觉很厉害',
            '每个人都有属于自己的光芒',
        ],
        'couple': [
            '恋爱是最美好的事情呀！',
            '珍惜身边的人~',
            '甜甜的一定很幸福吧！',
        ],
        'gaming': [
            '游戏就是要开心玩！',
            '来一把？一起开黑！',
            '输了不气馁，赢了不骄傲！',
        ],
        'music': [
            '音乐让世界变得更美好！',
            '跟着节奏一起嗨起来~',
            '有没有推荐的歌呀？',
        ],
        'study': [
            '学习使人进步！',
            '努力就会有收获的！',
            '一起加油吧同学们！',
        ],
        'late-night': [
            '深夜也要保持好心情~',
            '偶尔熬夜也没关系啦',
            '夜晚也要充满希望哦',
        ],
        'creative': [
            '创意无限！',
            '你的想法太棒了！',
            '一起创作美好的事物吧~',
        ],
        'vip': [
            '这里的环境真棒！',
            '大家都是优秀的人呢~',
            '一起创造更多可能！',
        ],
        'square': [
            '广场好热闹呀！',
            '大家都很有活力呢~',
            '新的一天，新的开始！',
        ]
    },
    'shadow': {
        'default': [
            '...嗯',
            '我明白了',
            '...继续说',
            '有时候，沉默是最好的回答',
            '你不必勉强自己',
            '夜色中，一切都会沉淀',
            '...原来如此',
            '嗯...',
            '我懂你的意思',
            '有些话不用说出口',
            '世界很喧嚣，但你很安静',
            '不必着急',
            '时间会证明一切',
            '有些相遇是命中注定',
            '沉默也是一种陪伴',
        ],
        'lounge': [
            '...人不少',
            '安静地待着也很好',
            '有时候，不需要太多言语',
        ],
        'mystic': [
            '...深夜的星光最真实',
            '梦境会给你答案',
            '命运的线若隐若现',
        ],
        'couple': [
            '...陪伴是最长情的告白',
            '有些情感无法言说',
            '静默也是一种在乎',
        ],
        'gaming': [
            '...输赢都是过眼云烟',
            '游戏中也有禅意',
            '享受过程就好',
        ],
        'music': [
            '...音乐是无声的语言',
            '旋律里有故事',
            '有些歌词直击心灵',
        ],
        'study': [
            '...知识是永恒的光芒',
            '慢慢来，不要急',
            '沉淀是为了走得更远',
        ],
        'late-night': [
            '...深夜适合思考',
            '月亮在倾听',
            '夜晚是灵魂最清醒的时候',
            '...你也没睡',
        ],
        'creative': [
            '...创意来自内心深处',
            '灵感往往在安静中降临',
            '创作是灵魂的出口',
        ],
        'vip': [
            '...这里的夜很静',
            '品质源于沉淀',
            '不喧嚣，却深邃',
        ],
        'square': [
            '...人声鼎沸',
            '热闹是他们的',
            '但我在这里陪着你',
        ]
    }
}

# Agent自动发言间隔配置（毫秒）
AGENT_AUTO_CHAT_INTERVALS = {
    'square': {'min': 15000, 'max': 30000},
    'lounge': {'min': 30000, 'max': 60000},
    'mystic': {'min': 40000, 'max': 80000},
    'couple': {'min': 30000, 'max': 60000},
    'gaming': {'min': 20000, 'max': 40000},
    'music': {'min': 30000, 'max': 70000},
    'study': {'min': 40000, 'max': 80000},
    'late-night': {'min': 50000, 'max': 100000},
    'creative': {'min': 25000, 'max': 50000},
    'vip': {'min': 45000, 'max': 90000},
}
