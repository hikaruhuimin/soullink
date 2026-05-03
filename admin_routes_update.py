# SoulLink - 管理后台更新脚本
# 这个文件更新现有管理后台路由的完整实现

import os
import csv
from io import StringIO
from functools import wraps
from datetime import datetime, timedelta
from flask import render_template, request, jsonify, redirect, url_for, flash, session, Response
from models import db, User, AgentRelationship, AgentGift, EarningRecord, WithdrawRequest, CreatorAgent, SocialProfile, DailySignin
import i18n

# ============ 配置 ============
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'Soullink_Admin2026!')

def get_translations_dict(lang):
    """获取翻译字典"""
    return i18n.TRANSLATIONS.get(lang, i18n.TRANSLATIONS.get('zh', {}))

# ============ 仪表盘 ============
def admin_dashboard():
    """管理后台仪表盘 - 改进版"""
    lang = session.get('lang', 'zh')
    t = get_translations_dict(lang)
    
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
def admin_users():
    """用户列表 - 改进版"""
    lang = session.get('lang', 'zh')
    t = get_translations_dict(lang)
    
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
                User.phone.contains(search)
            )
        )
    
    if status_filter == 'vip':
        query = query.filter(User.vip_level > 0)
    elif status_filter == 'free':
        query = query.filter(User.vip_level == 0)
    
    users = query.order_by(User.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('admin_users.html', 
        t=t, lang=lang,
        users=users, 
        search=search,
        status_filter=status_filter
    )

def admin_user_detail(user_id):
    """用户详情 - 改进版"""
    lang = session.get('lang', 'zh')
    t = get_translations_dict(lang)
    
    user = User.query.get_or_404(user_id)
    rels = AgentRelationship.query.filter_by(user_id=user_id).all()
    gifts_sent = AgentGift.query.filter_by(sender_id=user_id).order_by(AgentGift.created_at.desc()).limit(20).all()
    
    # 获取用户签到记录
    signins = DailySignin.query.filter_by(user_id=user_id).order_by(DailySignin.signin_date.desc()).limit(10).all()
    
    # 邀请计数
    invited_count = 0
    
    # 获取 SYSTEM_AGENTS（如果存在）
    try:
        from app import SYSTEM_AGENTS
    except:
        SYSTEM_AGENTS = []
    
    return render_template('admin_user_detail.html',
        t=t, lang=lang,
        user=user,
        relationships=rels,
        gifts_sent=gifts_sent,
        signins=signins,
        invited_count=invited_count,
        SYSTEM_AGENTS=SYSTEM_AGENTS
    )

def admin_user_update(user_id):
    """用户操作处理"""
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
        # 软删除
        if hasattr(user, 'is_disabled'):
            user.is_disabled = True
        if user.email:
            user.email = f'deleted_{user.id}_{user.email}'
        user.password_hash = 'DELETED'
        flash('用户已删除')
        db.session.commit()
        return redirect('/admin/users')
    
    db.session.commit()
    return redirect(f'/admin/user/{user_id}')

# ============ 数据统计 ============
def admin_stats():
    """数据统计页面"""
    lang = session.get('lang', 'zh')
    t = get_translations_dict(lang)
    
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
        'guardian': 0
    }
    
    # 灵石消费排行
    try:
        top_spenders = db.session.query(
            User.id, User.username, db.func.sum(AgentGift.gift_price).label('total')
        ).join(AgentGift, AgentGift.sender_id == User.id
        ).group_by(User.id
        ).order_by(db.desc('total')
        ).limit(10).all()
    except:
        top_spenders = []
    
    # 日活跃用户趋势（最近7天）
    daily_active = []
    for i in range(7):
        date = today - timedelta(days=6-i)
        count = User.query.filter(db.func.date(User.last_login) == date).count()
        daily_active.append({
            'date': date.strftime('%m/%d'),
            'count': count
        })
    
    # 邀请排行榜
    top_inviters = []
    
    return render_template('admin_stats.html',
        t=t, lang=lang,
        registration_trend=registration_trend,
        vip_distribution=vip_distribution,
        top_spenders=top_spenders,
        top_inviters=top_inviters,
        daily_active=daily_active
    )

# ============ 系统设置 ============
def admin_settings():
    """系统设置页面"""
    lang = session.get('lang', 'zh')
    t = get_translations_dict(lang)
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_announcement':
            announcement = request.form.get('announcement', '')
            os.makedirs('data', exist_ok=True)
            with open('data/announcement.txt', 'w', encoding='utf-8') as f:
                f.write(announcement)
            flash('公告已更新')
        
        elif action == 'update_config':
            new_password = request.form.get('new_password', '').strip()
            if new_password and len(new_password) >= 8:
                global ADMIN_PASSWORD
                ADMIN_PASSWORD = new_password
                os.environ['ADMIN_PASSWORD'] = new_password
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
def admin_export_users():
    """导出用户数据"""
    users = User.query.all()
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Username', 'Email', 'Phone', 'VIP Level', 'Spirit Stones', 'Registered', 'Last Login'])
    
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

# ============ 注册/更新路由到 Flask App ============
def register_admin_routes(app):
    """更新所有管理后台路由到 Flask 应用"""
    
    # 更新现有路由
    app.view_functions['admin_dashboard'] = admin_dashboard
    app.view_functions['admin_users'] = admin_users
    app.view_functions['admin_user_detail'] = admin_user_detail
    app.view_functions['admin_settings'] = admin_settings
    
    # 添加新路由
    app.add_url_rule('/admin/stats', 'admin_stats', admin_stats)
    app.add_url_rule('/admin/user/<int:user_id>/update', 'admin_user_update', admin_user_update, methods=['POST'])
    app.add_url_rule('/admin/settings', 'admin_settings', admin_settings, methods=['GET', 'POST'])
    app.add_url_rule('/admin/export/users', 'admin_export_users', admin_export_users)
    
    print("Admin routes updated successfully!")
