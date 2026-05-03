# SoulLink - 管理后台路由
# 包含仪表盘、用户管理、数据统计、系统设置等功能

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from functools import wraps
from datetime import datetime, timedelta
from models import db, User, AgentRelationship, AgentGift, EarningRecord, WithdrawRequest, CreatorAgent, SocialProfile, DailySignin
from i18n import get_translations

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# ============ 配置 ============
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'Soullink_Admin2026!'

# ============ 认证中间件 ============
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect('/admin/login')
        return f(*args, **kwargs)
    return decorated

def get_admin_lang():
    """获取管理员语言设置"""
    return session.get('lang', 'zh')

# ============ 认证路由 ============
@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect('/admin')
        flash('密码错误 / Wrong password / パスワードが間違っています')
    return render_template('admin_login.html')

@admin_bp.route('/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect('/admin/login')

# ============ 仪表盘 ============
@admin_bp.route('/')
@admin_required
def admin_dashboard():
    lang = get_admin_lang()
    t = get_translations(lang)
    
    # 用户统计
    total_users = User.query.count()
    
    # 今日新增用户
    today = datetime.utcnow().date()
    new_today = User.query.filter(
        db.func.date(User.created_at) == today
    ).count()
    
    # 活跃用户（7天内登录）
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    active_users = User.query.filter(
        User.last_login >= seven_days_ago
    ).count()
    
    # 总灵石流通量
    total_spirit_stones = db.session.query(db.func.sum(User.spirit_stones)).scalar() or 0
    
    # 会员用户数
    vip_users = User.query.filter(User.vip_level > 0).count()
    
    # 最近7天注册趋势
    registration_trend = []
    for i in range(7):
        date = today - timedelta(days=6-i)
        count = User.query.filter(db.func.date(User.created_at) == date).count()
        registration_trend.append({
            'date': date.strftime('%m/%d'),
            'count': count
        })
    
    # 最近注册用户
    recent_users = User.query.order_by(User.id.desc()).limit(10).all()
    
    # 礼物和收益统计
    total_gifts = AgentGift.query.count()
    total_earnings = EarningRecord.query.count() if 'EarningRecord' in dir() else 0
    
    return render_template('admin_dashboard.html',
        t=t, lang=lang,
        total_users=total_users,
        new_today=new_today,
        active_users=active_users,
        total_spirit_stones=total_spirit_stones,
        vip_users=vip_users,
        registration_trend=registration_trend,
        recent_users=recent_users,
        total_gifts=total_gifts,
        total_earnings=total_earnings
    )

# ============ 用户管理 ============
@admin_bp.route('/users')
@admin_required
def admin_users():
    lang = get_admin_lang()
    t = get_translations(lang)
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', 'all')
    
    query = User.query
    
    if search:
        query = query.filter(
            db.or_(
                User.username.contains(search),
                User.email.contains(search),
                User.phone.contains(search) if User.phone else False
            )
        )
    
    if status_filter == 'vip':
        query = query.filter(User.vip_level > 0)
    elif status_filter == 'free':
        query = query.filter(User.vip_level == 0)
    elif status_filter == 'disabled':
        query = query.filter(User.is_disabled == True) if hasattr(User, 'is_disabled') else query
    
    users = query.order_by(User.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('admin_users.html', 
        t=t, lang=lang,
        users=users, 
        search=search,
        status_filter=status_filter
    )

@admin_bp.route('/user/<int:user_id>')
@admin_required
def admin_user_detail(user_id):
    lang = get_admin_lang()
    t = get_translations(lang)
    
    user = User.query.get_or_404(user_id)
    rels = AgentRelationship.query.filter_by(user_id=user_id).all()
    gifts_sent = AgentGift.query.filter_by(sender_id=user_id).order_by(AgentGift.created_at.desc()).limit(20).all()
    
    # 获取用户邀请的好友数
    invited_count = User.query.filter_by(invited_by=user_id).count() if hasattr(User, 'invited_by') else 0
    
    # 获取用户签到记录
    signins = DailySignin.query.filter_by(user_id=user_id).order_by(DailySignin.signin_date.desc()).limit(10).all()
    
    return render_template('admin_user_detail.html',
        t=t, lang=lang,
        user=user,
        relationships=rels,
        gifts_sent=gifts_sent,
        invited_count=invited_count,
        signins=signins,
        SYSTEM_AGENTS=SYSTEM_AGENTS if 'SYSTEM_AGENTS' in dir() else []
    )

@admin_bp.route('/user/<int:user_id>/update', methods=['POST'])
@admin_required
def admin_user_update(user_id):
    user = User.query.get_or_404(user_id)
    action = request.form.get('action')
    
    if action == 'update_spirit':
        amount = request.form.get('amount', type=int)
        if amount is not None:
            user.spirit_stones = max(0, user.spirit_stones + amount)
            flash(f'已更新灵石余额: {"+" if amount >= 0 else ""}{amount}')
    
    elif action == 'set_spirit':
        amount = request.form.get('amount', type=int)
        if amount is not None:
            user.spirit_stones = max(0, amount)
            flash(f'已设置灵石余额为: {amount}')
    
    elif action == 'set_vip':
        level = request.form.get('level', type=int)
        expire_days = request.form.get('expire_days', type=int, default=30)
        if level is not None:
            user.vip_level = level
            if level > 0 and expire_days:
                user.vip_expire_date = datetime.utcnow() + timedelta(days=expire_days)
            flash(f'已设置VIP等级为: {level}')
    
    elif action == 'toggle_disabled':
        if hasattr(user, 'is_disabled'):
            user.is_disabled = not user.is_disabled
            flash(f'用户已{"禁用" if user.is_disabled else "启用"}')
        else:
            flash('该用户不支持此操作')
    
    elif action == 'delete':
        # 软删除：禁用并清除敏感信息
        user.is_disabled = True if hasattr(user, 'is_disabled') else None
        user.email = f'deleted_{user.id}_{user.email}'
        user.password_hash = 'DELETED'
        flash('用户已删除')
        db.session.commit()
        return redirect('/admin/users')
    
    db.session.commit()
    return redirect(f'/admin/user/{user_id}')

# ============ 数据统计 ============
@admin_bp.route('/stats')
@admin_required
def admin_stats():
    lang = get_admin_lang()
    t = get_translations(lang)
    
    # 用户注册趋势（最近30天）
    today = datetime.utcnow().date()
    registration_trend = []
    for i in range(30):
        date = today - timedelta(days=29-i)
        count = User.query.filter(db.func.date(User.created_at) == date).count()
        registration_trend.append({
            'date': date.strftime('%m/%d'),
            'count': count
        })
    
    # 会员分布
    vip_distribution = {
        'free': User.query.filter(User.vip_level == 0).count(),
        'basic': User.query.filter(User.vip_level == 1).count(),
        'premium': User.query.filter(User.vip_level == 2).count(),
        'guardian': User.query.filter(User.vip_level == 3).count() if hasattr(User, 'vip_level') else 0
    }
    
    # 灵石消费排行（通过礼物记录）
    top_spenders = db.session.query(
        User.id, User.username, db.func.sum(AgentGift.gift_price).label('total')
    ).join(AgentGift, AgentGift.sender_id == User.id
    ).group_by(User.id
    ).order_by(db.desc('total')
    ).limit(10).all()
    
    # 邀请排行榜（如果有邀请功能）
    if hasattr(User, 'invited_by'):
        top_inviters = db.session.query(
            User.id, User.username, db.func.count(User.id).label('invite_count')
        ).join(User, User.invited_by == User.id
        ).group_by(User.id
        ).order_by(db.desc('invite_count')
        ).limit(10).all()
    else:
        top_inviters = []
    
    # 日活跃用户趋势（最近7天）
    daily_active = []
    for i in range(7):
        date = today - timedelta(days=6-i)
        count = User.query.filter(db.func.date(User.last_login) == date).count()
        daily_active.append({
            'date': date.strftime('%m/%d'),
            'count': count
        })
    
    return render_template('admin_stats.html',
        t=t, lang=lang,
        registration_trend=registration_trend,
        vip_distribution=vip_distribution,
        top_spenders=top_spenders,
        top_inviters=top_inviters,
        daily_active=daily_active
    )

# ============ 系统设置 ============
@admin_bp.route('/settings', methods=['GET', 'POST'])
@admin_required
def admin_settings():
    lang = get_admin_lang()
    t = get_translations(lang)
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_announcement':
            announcement = request.form.get('announcement', '')
            # 保存公告到配置文件或数据库
            with open('data/announcement.txt', 'w', encoding='utf-8') as f:
                f.write(announcement)
            flash('公告已更新')
        
        elif action == 'update_config':
            # 更新其他配置
            new_password = request.form.get('new_password', '').strip()
            if new_password:
                global ADMIN_PASSWORD
                ADMIN_PASSWORD = new_password
                flash('管理员密码已更新')
    
    # 读取当前公告
    announcement = ''
    try:
        with open('data/announcement.txt', 'r', encoding='utf-8') as f:
            announcement = f.read()
    except:
        pass
    
    return render_template('admin_settings.html',
        t=t, lang=lang,
        announcement=announcement,
        admin_username=ADMIN_USERNAME
    )

# ============ 导出数据 ============
@admin_bp.route('/export/users')
@admin_required
def admin_export_users():
    import csv
    from io import StringIO
    
    users = User.query.all()
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', '用户名', '邮箱', '手机', 'VIP等级', '灵石', '注册时间', '最后登录'])
    
    for u in users:
        writer.writerow([
            u.id, u.username, u.email or '', u.phone or '',
            u.vip_level, u.spirit_stones,
            u.created_at.strftime('%Y-%m-%d') if u.created_at else '',
            u.last_login.strftime('%Y-%m-%d') if u.last_login else ''
        ])
    
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=users.csv'}
    )
