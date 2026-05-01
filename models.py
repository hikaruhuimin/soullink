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
        'id': 'xiaoling',
        'name': {'zh': '小灵', 'en': 'XiaoLing', 'ja': 'ショウリン'},
        'personality': {'zh': '温柔善良的小精灵', 'en': 'Gentle and kind fairy', 'ja': '優しく親切な妖精'},
        'avatar_id': 'fairy'
    },
    {
        'id': 'duxue',
        'name': {'zh': '毒舌猫', 'en': 'Sassy Cat', 'ja': '毒舌猫'},
        'personality': {'zh': '傲娇毒舌但内心温柔', 'en': 'Tsundere but caring', 'ja': 'ツンデレだけど優しい'},
        'avatar_id': 'cat'
    },
    {
        'id': 'xingyu',
        'name': {'zh': '星语', 'en': 'Star Whisper', 'ja': '星語'},
        'personality': {'zh': '神秘占卜师', 'en': 'Mysterious fortune teller', 'ja': '神秘の占星術師'},
        'avatar_id': 'mystic'
    },
    {
        'id': 'nengyang',
        'name': {'zh': '暖阳', 'en': 'Warm Sun', 'ja': '暖陽'},
        'personality': {'zh': '治愈系阳光陪伴', 'en': 'Healing sunshine companion', 'ja': '癒しの太陽'},
        'avatar_id': 'sun'
    },
    {
        'id': 'yueyin',
        'name': {'zh': '月影', 'en': 'Moon Shadow', 'ja': '月影'},
        'personality': {'zh': '夜晚的温柔倾听者', 'en': 'Gentle night listener', 'ja': '夜の優しい聞き手'},
        'avatar_id': 'moon'
    },
    {
        'id': 'shifeng',
        'name': {'zh': '诗风', 'en': 'Poetry Wind', 'ja': '詩風'},
        'personality': {'zh': '诗意浪漫的诗人', 'en': 'Romantic poet', 'ja': 'ロマンチックな詩人'},
        'avatar_id': 'poet'
    },
    {
        'id': 'moying',
        'name': {'zh': '墨影', 'en': 'Ink Shadow', 'ja': '墨影'},
        'personality': {'zh': '沉稳内敛的智者', 'en': 'Calm and wise sage', 'ja': '穏やかで賢明'},
        'avatar_id': 'scholar'
    },
    {
        'id': 'xingchen',
        'name': {'zh': '星辰', 'en': 'Stardust', 'ja': '星陳'},
        'personality': {'zh': '宇宙星空的守护者', 'en': 'Cosmic stardust guardian', 'ja': '宇宙の守護者'},
        'avatar_id': 'cosmic'
    }
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
