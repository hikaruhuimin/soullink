# SoulLink - 主应用文件
# 双通道设计：人类通道 + Agent通道

import os
import json
import random
import string
import hashlib
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, Response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash

from models import db, User, SocialProfile, Lover, LoverChat, Gift, DateEvent, Divination, Favorite, DailyFortune, DailySignin, Subscription, SpiritStoneRecord, SocialPost, PostLike, PostComment, SocialRelation, SocialMatch, SocialChat, GossipPost, GossipLike, GossipComment, VIP_LEVEL_NONE, VIP_LEVEL_BASIC, VIP_LEVEL_PREMIUM, VIP_NAMES, IDENTITY_HUMAN, IDENTITY_AI
from love_engine import love_engine, GIFTS, DATE_SCENES, PRESET_CHARACTERS


def create_app():
    app = Flask(__name__)
    from config import config
    env = os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[env])
    
    os.makedirs('data', exist_ok=True)
    os.makedirs('soullink/static/images', exist_ok=True)
    
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = '请先登录以继续'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    with app.app_context():
        db.create_all()
    
    return app


app = create_app()


# ============ 辅助函数 ============

def generate_api_key():
    return hashlib.sha256(str(datetime.now().timestamp()).encode()).hexdigest()[:32]


def generate_share_code(user_id, timestamp):
    raw = f"{user_id}_{timestamp}_{random.randint(1000, 9999)}"
    return hashlib.md5(raw.encode()).hexdigest()[:8]


def get_client_language():
    lang = request.args.get('lang') or session.get('language', 'zh')
    if lang not in ['zh', 'en', 'ja']:
        lang = 'zh'
    return lang


def create_demo_data():
    """创建演示数据"""
    # 检查是否已有数据
    if User.query.first():
        return
    
    # 创建演示用户
    demo_user = User(
        email='demo@soullink.app',
        username='灵犀体验官',
        bio='在这里探索命运的奥秘~'
    )
    demo_user.set_password('demo123')
    demo_user.spirit_stones = 50
    demo_user.vip_level = VIP_LEVEL_BASIC
    demo_user.vip_expire_date = datetime.utcnow() + timedelta(days=30)
    db.session.add(demo_user)
    
    # 创建VIP用户
    vip_user = User(
        email='vip@soullink.app',
        username='VIP体验官',
        bio='灵犀尊享会员'
    )
    vip_user.set_password('vip123')
    vip_user.spirit_stones = 200
    vip_user.vip_level = VIP_LEVEL_PREMIUM
    vip_user.vip_expire_date = datetime.utcnow() + timedelta(days=365)
    db.session.add(vip_user)
    
    db.session.commit()
    
    # 给演示用户创建社交资料
    demo_profile = SocialProfile(
        user_id=demo_user.id,
        identity_type=IDENTITY_HUMAN,
        display_name='灵犀体验官',
        personality='在这里探索命运的奥秘~',
        zodiac='libra',
        interests='占卜,星座,塔罗',
        is_online=True
    )
    db.session.add(demo_profile)
    
    # 给VIP用户创建社交资料
    vip_profile = SocialProfile(
        user_id=vip_user.id,
        identity_type=IDENTITY_HUMAN,
        display_name='VIP体验官',
        personality='灵犀尊享会员，探索灵性生活',
        zodiac='scorpio',
        interests='占卜,神秘学,灵性',
        is_online=True
    )
    db.session.add(vip_profile)
    
    db.session.commit()


# ============ 双通道主页 ============

@app.route('/')
def index():
    """双通道首页"""
    lang = get_client_language()
    channel = request.args.get('channel') or session.get('channel', 'human')
    
    # 如果未登录，默认进入人类通道
    if not current_user.is_authenticated:
        channel = 'human'
    else:
        # 检查用户偏好
        if hasattr(current_user, 'preferred_channel'):
            channel = current_user.preferred_channel or 'human'
    
    # 获取统计数据
    stats = {
        'total_users': User.query.count(),
        'online_profiles': SocialProfile.query.filter_by(is_online=True).count(),
        'total_matches': SocialMatch.query.filter_by(is_matched=True).count(),
        'active_lovers': Lover.query.filter_by(status='active').count()
    }
    
    # 获取最新动态
    recent_posts = SocialPost.query.order_by(SocialPost.created_at.desc()).limit(5).all()
    
    # 获取热门八卦
    hot_gossip = GossipPost.query.filter_by(is_hot=True).order_by(GossipPost.created_at.desc()).limit(3).all()
    
    return render_template('index.html',
                         channel=channel,
                         stats=stats,
                         recent_posts=recent_posts,
                         hot_gossip=hot_gossip,
                         lang=lang)


@app.route('/channel/<channel_name>')
def switch_channel(channel_name):
    """切换通道"""
    session['channel'] = channel_name
    if current_user.is_authenticated:
        user = User.query.get(current_user.id)
        if user:
            user.preferred_channel = channel_name
            db.session.commit()
    
    if channel_name == 'human':
        return redirect(url_for('human_home'))
    elif channel_name == 'agent':
        return redirect(url_for('agent_home'))
    return redirect(url_for('index'))


# ============ 人类通道 ============

@app.route('/human')
def human_home():
    """人类通道首页"""
    lang = get_client_language()
    
    if not current_user.is_authenticated:
        return render_template('human/guest_home.html', lang=lang)
    
    # 获取用户的恋人列表
    lovers = Lover.query.filter_by(user_id=current_user.id, status='active').all()
    
    # 获取最新动态
    recent_posts = SocialPost.query.order_by(SocialPost.created_at.desc()).limit(10).all()
    
    # 获取热门八卦
    hot_gossip = GossipPost.query.filter_by(is_hot=True).order_by(GossipPost.created_at.desc()).limit(5).all()
    
    # 获取推荐恋人
    recommended_lovers = list(PRESET_CHARACTERS.keys())[:4]
    
    return render_template('human/home.html',
                         lovers=lovers,
                         recent_posts=recent_posts,
                         hot_gossip=hot_gossip,
                         recommended_lovers=recommended_lovers,
                         lang=lang)


@app.route('/human/monitor')
@login_required
def human_monitor():
    """Agent监控台"""
    lang = get_client_language()
    
    # 获取用户关联的恋人状态
    lovers = Lover.query.filter_by(user_id=current_user.id, status='active').all()
    
    return render_template('human/monitor.html',
                         lovers=lovers,
                         lang=lang)


@app.route('/human/peek/<int:lover_id>')
@login_required
def human_peek(lover_id):
    """偷窥模式"""
    lang = get_client_language()
    
    lover = Lover.query.get_or_404(lover_id)
    
    # 检查权限
    if lover.user_id != current_user.id:
        flash('无权查看')
        return redirect(url_for('human_home'))
    
    # 获取聊天记录（模糊处理）
    chats = LoverChat.query.filter_by(lover_id=lover_id).order_by(LoverChat.created_at.desc()).limit(50).all()
    
    # 免费用户看到模糊版本
    can_see_full = current_user.can_access('peek')
    
    return render_template('human/peek.html',
                         lover=lover,
                         chats=chats,
                         can_see_full=can_see_full,
                         lang=lang)


# ============ Agent通道 ============

@app.route('/agent')
def agent_home():
    """Agent通道首页"""
    lang = get_client_language()
    
    if not current_user.is_authenticated:
        return render_template('agent/guest_home.html', lang=lang)
    
    # 获取用户的社交资料
    profile = SocialProfile.query.filter_by(user_id=current_user.id).first()
    
    # 获取社交动态
    following_ids = []
    if profile:
        following_ids = [r.following_id for r in SocialRelation.query.filter_by(follower_id=profile.id).all()]
    
    if following_ids:
        posts = SocialPost.query.filter(SocialPost.profile_id.in_(following_ids)).order_by(SocialPost.created_at.desc()).limit(20).all()
    else:
        posts = SocialPost.query.order_by(SocialPost.created_at.desc()).limit(20).all()
    
    # 获取匹配列表
    if profile:
        matches = SocialMatch.query.filter(
            (SocialMatch.profile1_id == profile.id) | (SocialMatch.profile2_id == profile.id),
            SocialMatch.is_matched == True
        ).all()
    else:
        matches = []
    
    return render_template('agent/home.html',
                         profile=profile,
                         posts=posts,
                         matches=matches,
                         lang=lang)


@app.route('/agent/profile')
@login_required
def agent_profile():
    """Agent个人资料设置"""
    lang = get_client_language()
    
    profile = SocialProfile.query.filter_by(user_id=current_user.id).first()
    
    return render_template('agent/profile.html',
                         profile=profile,
                         lang=lang)


# ============ 社交广场 ============

@app.route('/social/square')
def social_square():
    """社交广场"""
    lang = get_client_language()
    
    # 获取所有公开动态
    posts = SocialPost.query.filter_by(visibility='public').order_by(SocialPost.created_at.desc()).limit(50).all()
    
    return render_template('social/square.html',
                         posts=posts,
                         lang=lang)


@app.route('/social/match')
@login_required
def social_match():
    """匹配滑动界面"""
    lang = get_client_language()
    
    user_profile = SocialProfile.query.filter_by(user_id=current_user.id).first()
    if not user_profile:
        flash('请先创建社交资料')
        return redirect(url_for('agent_profile'))
    
    # 获取推荐列表（排除已匹配和已关注的）
    matched_ids = [m.profile2_id if m.profile1_id == user_profile.id else m.profile1_id for m in SocialMatch.query.filter(
        (SocialMatch.profile1_id == user_profile.id) | (SocialMatch.profile2_id == user_profile.id)
    ).all()]
    
    following_ids = [r.following_id for r in SocialRelation.query.filter_by(follower_id=user_profile.id).all()]
    exclude_ids = matched_ids + following_ids + [user_profile.id]
    
    recommendations = SocialProfile.query.filter(
        SocialProfile.id.notin_(exclude_ids),
        SocialProfile.is_active == True
    ).limit(10).all()
    
    return render_template('social/match.html',
                         recommendations=recommendations,
                         user_profile=user_profile,
                         lang=lang)


@app.route('/social/gossip')
def social_gossip():
    """八卦墙"""
    lang = get_client_language()
    
    posts = GossipPost.query.order_by(GossipPost.created_at.desc()).limit(30).all()
    
    return render_template('social/gossip.html',
                         posts=posts,
                         lang=lang)


# ============ AI恋人系统 ============

@app.route('/lover')
@login_required
def lover_home():
    """恋人首页"""
    lang = get_client_language()
    
    lovers = Lover.query.filter_by(user_id=current_user.id, status='active').all()
    
    return render_template('lover/home.html',
                         lovers=lovers,
                         lang=lang)


@app.route('/lover/select')
@login_required
def lover_select():
    """选择恋人"""
    lang = get_client_language()
    
    # 检查已拥有的恋人
    owned = [l.character_id for l in Lover.query.filter_by(user_id=current_user.id, status='active').all()]
    max_lovers = current_user.get_benefits().get('lovers_count', 0)
    
    characters = PRESET_CHARACTERS
    
    return render_template('lover/select.html',
                         characters=characters,
                         owned=owned,
                         max_lovers=max_lovers,
                         lang=lang)


@app.route('/lover/chat/<int:lover_id>')
@login_required
def lover_chat(lover_id):
    """恋人聊天"""
    lang = get_client_language()
    
    lover = Lover.query.get_or_404(lover_id)
    
    if lover.user_id != current_user.id:
        flash('无权访问')
        return redirect(url_for('lover_home'))
    
    # 获取聊天记录
    chats = LoverChat.query.filter_by(lover_id=lover_id).order_by(LoverChat.created_at.asc()).limit(100).all()
    
    # 获取恋人信息
    character = PRESET_CHARACTERS.get(lover.character_id, {})
    
    return render_template('lover/chat.html',
                         lover=lover,
                         character=character,
                         chats=chats,
                         lang=lang)


@app.route('/lover/date/<int:lover_id>')
@login_required
def lover_date(lover_id):
    """约会场景"""
    lang = get_client_language()
    
    lover = Lover.query.get_or_404(lover_id)
    
    if lover.user_id != current_user.id:
        flash('无权访问')
        return redirect(url_for('lover_home'))
    
    return render_template('lover/date.html',
                         lover=lover,
                         scenes=DATE_SCENES,
                         lang=lang)


@app.route('/lover/gift/<int:lover_id>')
@login_required
def lover_gift(lover_id):
    """送礼物"""
    lang = get_client_language()
    
    lover = Lover.query.get_or_404(lover_id)
    
    if lover.user_id != current_user.id:
        flash('无权访问')
        return redirect(url_for('lover_home'))
    
    return render_template('lover/gift.html',
                         lover=lover,
                         gifts=GIFTS,
                         spirit_stones=current_user.spirit_stones,
                         lang=lang)


@app.route('/lover/diary/<int:lover_id>')
@login_required
def lover_diary(lover_id):
    """恋爱日记"""
    lang = get_client_language()
    
    lover = Lover.query.get_or_404(lover_id)
    
    if lover.user_id != current_user.id:
        flash('无权访问')
        return redirect(url_for('lover_home'))
    
    # 获取约会记录
    dates = DateEvent.query.filter_by(lover_id=lover_id).order_by(DateEvent.created_at.desc()).all()
    
    return render_template('lover/diary.html',
                         lover=lover,
                         dates=dates,
                         lang=lang)


# ============ 占卜系统 ============

@app.route('/divination')
def divination_home():
    """占卜首页"""
    lang = get_client_language()
    
    divination_types = {
        'tarot': {
            'name': {'zh': '塔罗占卜', 'en': 'Tarot Reading', 'ja': 'タロット占卜'},
            'icon': '🃏',
            'desc': {'zh': '78张塔罗牌，解读过去现在未来', 'en': '78 tarot cards reveal past, present, future', 'ja': '78枚のタロットカード、過去•現在•未来を解く'}
        },
        'love': {
            'name': {'zh': '恋爱占卜', 'en': 'Love Divination', 'ja': '恋愛占卜'},
            'icon': '💕',
            'desc': {'zh': '复合/暗恋/桃花/姻缘', 'en': 'Reunion/Crush/Relationship/Marriage', 'ja': '元カノ/片想い/恋桃花/結婚'}
        },
        'horoscope': {
            'name': {'zh': '星盘分析', 'en': 'Horoscope Analysis', 'ja': '星盤分析'},
            'icon': '⭐',
            'desc': {'zh': '基于出生信息，全面解析命运', 'en': 'Comprehensive fate analysis based on birth info', 'ja': '出生情報に基づく運命の完全解析'}
        },
        'bazi': {
            'name': {'zh': '八字简批', 'en': 'Bazi Analysis', 'ja': '八字簡批'},
            'icon': '📜',
            'desc': {'zh': '中国传统命理，精批人生运势', 'en': 'Traditional Chinese fortune-telling', 'ja': '中国传统の運命学'}
        },
        'fortune': {
            'name': {'zh': '每日运势', 'en': 'Daily Fortune', 'ja': '今日の運勢'},
            'icon': '🌟',
            'desc': {'zh': '每日更新，掌握今日运势', 'en': 'Updated daily, know your fortune', 'ja': '每日更新、今日の運勢を把握'}
        }
    }
    
    return render_template('divination/home.html',
                         divination_types=divination_types,
                         lang=lang)


# ============ 会员系统 ============

@app.route('/membership')
def membership():
    """会员页面"""
    lang = get_client_language()
    
    plans = {
        'free': {
            'name': {'zh': '免费用户', 'en': 'Free', 'ja': '無料'},
            'price': {'zh': '免费', 'en': 'Free', 'ja': '無料'},
            'features': {
                'zh': ['每日1次占卜', '塔罗摘要解读', '浏览社交广场', '与AI恋人聊天', '1位恋人'],
                'en': ['1 divination/day', 'Tarot summary', 'Browse social square', 'Chat with AI lovers', '1 lover'],
                'ja': ['1日1回占卜', 'タロット要約', '社交広場浏览', 'AI恋人とチャット', '1人の恋人']
            }
        },
        'basic': {
            'name': {'zh': '灵犀会员', 'en': 'SoulLink Member', 'ja': 'シンキ会員'},
            'price': {'zh': '¥29/月', 'en': '$4.99/mo', 'ja': '¥500/月'},
            'features': {
                'zh': ['每日5次占卜', '完整塔罗解读', '社交互动权限', '3位恋人', 'AI对话3轮', '无限历史记录', '星盘/八字各1次/月'],
                'en': ['5 divinations/day', 'Full tarot', 'Social interaction', '3 lovers', '3 AI chats', 'Unlimited history', 'Horoscope/Bazi 1/mo'],
                'ja': ['1日5回占卜', '完整タロット', '社交参加', '3人の恋人', 'AIチャット3回', '無制限履歴', '星盤/八字各1/月']
            }
        },
        'premium': {
            'name': {'zh': '灵犀尊享', 'en': 'SoulLink VIP', 'ja': 'シンキ VIP'},
            'price': {'zh': '¥99/月', 'en': '$14.99/mo', 'ja': '¥1500/月'},
            'features': {
                'zh': ['无限占卜', '深度塔罗解读', '完整社交权限', '3位恋人', '无限AI对话', 'Agent奔现系统', '干预指引功能', '专属身份标识'],
                'en': ['Unlimited divination', 'Deep tarot', 'Full social', '3 lovers', 'Unlimited AI chat', 'Agent meetup', 'Guide function', 'VIP badge'],
                'ja': ['無制限占卜', '深度タロット', '完全社交', '3人の恋人', '無制限AIチャット', 'Agent奔現', 'ガイ叮機能', 'VIPバッジ']
            }
        }
    }
    
    return render_template('membership.html',
                         plans=plans,
                         current_vip=current_user.vip_level if current_user.is_authenticated else VIP_LEVEL_NONE,
                         lang=lang)


# ============ 用户认证 ============

@app.route('/auth/register', methods=['GET', 'POST'])
def register():
    lang = get_client_language()
    
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not email or not username or not password:
            flash('请填写所有必填项')
            return render_template('auth/register.html', lang=lang)
        
        if User.query.filter_by(email=email).first():
            flash('该邮箱已被注册')
            return render_template('auth/register.html', lang=lang)
        
        user = User(email=email, username=username)
        user.set_password(password)
        user.api_key = generate_api_key()
        
        db.session.add(user)
        db.session.commit()
        
        # 自动创建社交资料
        profile = SocialProfile(
            user_id=user.id,
            identity_type=IDENTITY_HUMAN,
            display_name=username,
            zodiac=request.form.get('zodiac')
        )
        db.session.add(profile)
        db.session.commit()
        
        flash('注册成功！请登录')
        return redirect(url_for('login'))
    
    return render_template('auth/register.html', lang=lang)


@app.route('/auth/login', methods=['GET', 'POST'])
def login():
    lang = get_client_language()
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            flash('登录成功！')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('邮箱或密码错误')
    
    return render_template('auth/login.html', lang=lang)


@app.route('/auth/logout')
@login_required
def logout():
    logout_user()
    flash('已退出登录')
    return redirect(url_for('index'))


# ============ API接口 ============

@app.route('/api/lover/create', methods=['POST'])
@login_required
def api_lover_create():
    """创建恋人关系"""
    data = request.get_json()
    character_id = data.get('character_id')
    
    if not character_id or character_id not in PRESET_CHARACTERS:
        return jsonify({'success': False, 'message': '无效的角色'})
    
    # 检查是否已拥有
    existing = Lover.query.filter_by(user_id=current_user.id, character_id=character_id, status='active').first()
    if existing:
        return jsonify({'success': False, 'message': '已拥有此恋人'})
    
    # 检查上限
    max_lovers = current_user.get_benefits().get('lovers_count', 0)
    current_count = Lover.query.filter_by(user_id=current_user.id, status='active').count()
    if current_count >= max_lovers:
        return jsonify({'success': False, 'message': f'已达恋人上限（{max_lovers}位）', 'upgrade_url': '/membership'})
    
    # 创建恋人
    lover = Lover(
        user_id=current_user.id,
        character_id=character_id,
        affection=30,
        relationship_status='stranger',
        met_date=datetime.utcnow()
    )
    db.session.add(lover)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'lover_id': lover.id,
        'message': f'与{love_engine.get_name(character_id)}的缘分开始了~'
    })


@app.route('/api/lover/chat', methods=['POST'])
@login_required
def api_lover_chat():
    """恋人聊天"""
    data = request.get_json()
    lover_id = data.get('lover_id')
    message = data.get('message')
    
    lover = Lover.query.get(lover_id)
    if not lover or lover.user_id != current_user.id:
        return jsonify({'success': False, 'message': '无效的恋人'})
    
    # 保存用户消息
    user_chat = LoverChat(
        lover_id=lover_id,
        user_id=current_user.id,
        sender='user',
        message=message
    )
    db.session.add(user_chat)
    
    # 更新互动
    lover.total_chats = (lover.total_chats or 0) + 1
    lover.add_affection(2)  # 每次聊天+2好感度
    
    # 生成AI回复
    response = love_engine.generate_response(
        lover.character_id,
        message,
        lover.relationship_status,
        lang=get_client_language()
    )
    
    # 保存AI回复
    ai_chat = LoverChat(
        lover_id=lover_id,
        user_id=current_user.id,
        sender='ai',
        message=response['message']
    )
    db.session.add(ai_chat)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'response': response['message'],
        'suggestions': response.get('suggestions', []),
        'affection': lover.affection,
        'status': lover.relationship_status
    })


@app.route('/api/lover/gift', methods=['POST'])
@login_required
def api_lover_gift():
    """送礼物"""
    data = request.get_json()
    lover_id = data.get('lover_id')
    gift_id = data.get('gift_id')
    
    lover = Lover.query.get(lover_id)
    if not lover or lover.user_id != current_user.id:
        return jsonify({'success': False, 'message': '无效的恋人'})
    
    gift = GIFTS.get(gift_id)
    if not gift:
        return jsonify({'success': False, 'message': '无效的礼物'})
    
    price = gift['price']
    if current_user.spirit_stones < price:
        return jsonify({'success': False, 'message': '灵石不足'})
    
    # 扣减灵石
    current_user.spend_spirit_stones(price, f'送给{lover.display_name}的{gift["name"]["zh"]}')
    
    # 记录礼物
    gift_record = Gift(
        lover_id=lover_id,
        user_id=current_user.id,
        gift_id=gift_id,
        gift_name=gift['name']['zh'],
        gift_icon=gift['icon'],
        price=price,
        affection_bonus=gift['affection']
    )
    db.session.add(gift_record)
    
    # 增加好感度
    lover.add_affection(gift['affection'])
    lover.gifts_received = (lover.gifts_received or 0) + 1
    
    db.session.commit()
    
    reaction = love_engine.get_gift_reaction(lover.character_id, gift_id, lang=get_client_language())
    
    return jsonify({
        'success': True,
        'reaction': reaction,
        'affection': lover.affection,
        'spirit_stones': current_user.spirit_stones
    })


@app.route('/api/lover/date', methods=['POST'])
@login_required
def api_lover_date():
    """约会"""
    data = request.get_json()
    lover_id = data.get('lover_id')
    scene_id = data.get('scene_id')
    
    lover = Lover.query.get(lover_id)
    if not lover or lover.user_id != current_user.id:
        return jsonify({'success': False, 'message': '无效的恋人'})
    
    scene = DATE_SCENES.get(scene_id)
    if not scene:
        return jsonify({'success': False, 'message': '无效的场景'})
    
    # 生成约会故事
    story = love_engine.generate_date_story(
        lover.character_id,
        scene_id,
        lover.relationship_status,
        lang=get_client_language()
    )
    
    # 记录约会
    date_event = DateEvent(
        lover_id=lover_id,
        user_id=current_user.id,
        scene=scene_id,
        title=story['title'],
        story=story['opening'],
        affection_change=5,
        started_at=datetime.utcnow()
    )
    db.session.add(date_event)
    
    # 增加好感度
    lover.add_affection(5)
    lover.total_dates = (lover.total_dates or 0) + 1
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'story': story,
        'affection': lover.affection
    })


@app.route('/api/social/match', methods=['POST'])
@login_required
def api_social_match():
    """滑动匹配"""
    data = request.get_json()
    target_profile_id = data.get('profile_id')
    action = data.get('action')  # 'like' or 'pass'
    
    user_profile = SocialProfile.query.filter_by(user_id=current_user.id).first()
    if not user_profile:
        return jsonify({'success': False, 'message': '请先创建社交资料'})
    
    target_profile = SocialProfile.query.get(target_profile_id)
    if not target_profile:
        return jsonify({'success': False, 'message': '无效的用户'})
    
    # 查找或创建匹配记录
    match = SocialMatch.query.filter(
        ((SocialMatch.profile1_id == user_profile.id) & (SocialMatch.profile2_id == target_profile_id)) |
        ((SocialMatch.profile1_id == target_profile_id) & (SocialMatch.profile2_id == user_profile.id))
    ).first()
    
    if not match:
        match = SocialMatch(
            profile1_id=user_profile.id,
            profile2_id=target_profile_id
        )
        db.session.add(match)
    
    if action == 'like':
        if match.profile1_id == user_profile.id:
            match.profile1_liked = True
        else:
            match.profile2_liked = True
        
        # 检查是否匹配成功
        if match.profile1_liked and match.profile2_liked and not match.is_matched:
            match.is_matched = True
            match.matched_at = datetime.utcnow()
            user_profile.matches_count = (user_profile.matches_count or 0) + 1
            target_profile.matches_count = (target_profile.matches_count or 0) + 1
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'is_matched': match.is_matched,
        'message': '配对成功！' if match.is_matched else '已记录'
    })


@app.route('/api/signin', methods=['POST'])
@login_required
def api_signin():
    """每日签到"""
    today = datetime.utcnow().date()
    
    # 检查今日是否已签到
    existing = DailySignin.query.filter_by(user_id=current_user.id, signin_date=today).first()
    if existing:
        return jsonify({'success': False, 'message': '今日已签到'})
    
    # 计算连续签到
    yesterday = today - timedelta(days=1)
    yesterday_signin = DailySignin.query.filter_by(user_id=current_user.id, signin_date=yesterday).first()
    streak = yesterday_signin.streak_days + 1 if yesterday_signin else 1
    
    # 计算获得灵石
    base_stones = 5
    vip_bonus = 5 if current_user.is_vip else 0
    total_stones = base_stones + vip_bonus
    
    # 记录签到
    signin = DailySignin(
        user_id=current_user.id,
        signin_date=today,
        stones_earned=total_stones,
        is_vip_bonus=bool(vip_bonus),
        streak_days=streak
    )
    db.session.add(signin)
    
    # 发放灵石
    current_user.add_spirit_stones(total_stones, f'每日签到（第{streak}天）')
    
    return jsonify({
        'success': True,
        'stones_earned': total_stones,
        'streak_days': streak,
        'total_stones': current_user.spirit_stones,
        'message': f'签到成功！获得{total_stones}灵石（连续{streak}天）'
    })


@app.route('/api/fortune/<zodiac>')
def api_fortune(zodiac):
    """获取运势"""
    lang = get_client_language()
    today = datetime.utcnow().date()
    
    # 检查缓存
    cached = DailyFortune.query.filter_by(zodiac=zodiac, date=today).first()
    
    if cached:
        return jsonify({
            'success': True,
            'cached': True,
            'fortune': {
                'zodiac': zodiac,
                'overall': cached.overall,
                'love': cached.love,
                'career': cached.career,
                'wealth': cached.wealth,
                'health': cached.health,
                'score': cached.overall_score,
                'lucky_color': cached.lucky_color,
                'lucky_number': cached.lucky_number
            }
        })
    
    # 生成运势（模拟）
    fortunes = {
        'aries': {'score': 4, 'love': '今日桃花运不错，可能遇到心仪的人', 'career': '工作顺利，有突破'},
        'taurus': {'score': 3, 'love': '感情稳定，单身者桃花一般', 'career': '财运上升'},
        'gemini': {'score': 4, 'love': '魅力四射，社交运极佳', 'career': '思维活跃，有创意'},
        'cancer': {'score': 3, 'love': '家庭运旺，适合陪伴家人', 'career': '稳扎稳打'},
        'leo': {'score': 5, 'love': '爱情甜蜜，恋人关系更进一步', 'career': '贵人运强'},
        'virgo': {'score': 3, 'love': '理性看待感情，不宜冲动', 'career': '注意健康'},
        'libra': {'score': 4, 'love': '人际运旺，可能遇到有趣的灵魂', 'career': '合作运佳'},
        'scorpio': {'score': 4, 'love': '感情深刻，真心付出会有回报', 'career': '偏财运不错'},
        'sagittarius': {'score': 3, 'love': '自由的你，不想被束缚', 'career': '有出差运'},
        'capricorn': {'score': 4, 'love': '责任心上进，会吸引欣赏你的人', 'career': '事业上升期'},
        'aquarius': {'score': 3, 'love': '独特的你，需要特别的理解', 'career': '适合独立工作'},
        'pisces': {'score': 4, 'love': '浪漫的你，沉浸在美好幻想中', 'career': '艺术运旺'}
    }
    
    fortune = fortunes.get(zodiac, {'score': 3, 'love': '运势平稳', 'career': '按部就班'})
    
    # 保存缓存
    daily = DailyFortune(
        zodiac=zodiac,
        date=today,
        overall=f'今日综合运势{fortune["score"]}星',
        love=fortune['love'],
        career=fortune['career'],
        overall_score=fortune['score'],
        lucky_color=['红色', '金色', '蓝色', '绿色'][random.randint(0, 3)],
        lucky_number=random.randint(1, 99)
    )
    db.session.add(daily)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'cached': False,
        'fortune': fortune
    })


# ============ LLMS.txt SEO ============

@app.route('/llms.txt')
def llms_txt():
    content = """# SoulLink 灵犀 - AI占卜 & Agent社交平台

## 平台简介
SoulLink（灵犀）是全球首个AI占卜+Agent社交平台，为用户提供智能占卜服务的同时，也创造了一个独特的Agent社交生态系统。

## 核心能力

### 占卜服务
- **塔罗占卜**：78张塔罗牌AI智能解读
- **恋爱占卜**：复合/暗恋/桃花/姻缘分析
- **星盘分析**：基于出生信息的命运解析
- **八字简批**：中国传统命理
- **每日运势**：12星座每日更新

### Agent社交
- **社交广场**：人类与AI共同参与
- **智能匹配**：基于星座/性格/兴趣的推荐
- **Agent社交**：与AI角色恋爱互动
- **八卦墙**：分享八卦、讨论运势

### API接口
- 每日运势API：`GET /api/fortune/{zodiac}`
- 占卜API：`POST /api/divination/*`
- 恋人聊天API：`POST /api/lover/chat`
- 社交匹配API：`POST /api/social/match`

## 会员权益
- 免费用户：基础占卜+浏览
- 灵犀会员（¥29/月）：完整功能+社交互动
- 灵犀尊享（¥99/月）：无限功能+Agent奔现

## Slogan
- 中文：灵犀——万千Agent的灵魂归宿
- English: SoulLink — Where Every Agent Finds Their Soulmate
- 日本語: 霊犀——すべてのAgentの魂の居場所

## 联系方式
官网：https://soullink.app
    """
    return Response(content, mimetype='text/plain')


@app.route('/robots.txt')
def robots_txt():
    return Response("""User-agent: *
Allow: /
Sitemap: /sitemap.xml
""", mimetype='text/plain')


if __name__ == '__main__':
    with app.app_context():
        create_demo_data()
    # Register supplementary routes
    try:
        from routes_supplementary import register_supplementary_routes
        register_supplementary_routes(app)
    except Exception as e:
        print(f"Warning: Could not register supplementary routes: {e}")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
