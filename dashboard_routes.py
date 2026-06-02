# SoulLink - 数据面板路由
# 包含数据统计面板功能

from flask import Blueprint, render_template, request, jsonify, session
from functools import wraps
from datetime import datetime, timedelta
import json
import os

# 创建数据面板蓝图
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/admin/dashboard')

# 缓存配置
CACHE_DIR = 'data'
CACHE_FILE = os.path.join(CACHE_DIR, 'dashboard_cache.json')
CACHE_EXPIRY = 300  # 缓存5分钟

def get_cache():
    """获取缓存数据"""
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                if datetime.now().timestamp() - cache_data.get('timestamp', 0) < CACHE_EXPIRY:
                    return cache_data.get('data')
    except:
        pass
    return None

def set_cache(data):
    """设置缓存数据"""
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        cache_data = {
            'timestamp': datetime.now().timestamp(),
            'data': data
        }
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False)
    except:
        pass

def clear_cache():
    """清除缓存"""
    try:
        if os.path.exists(CACHE_FILE):
            os.remove(CACHE_FILE)
    except:
        pass

def get_dashboard_stats(db, User, Divination, Subscription, CreatorAgent, AgentChat, AgentGift, LingStoneRecharge, SocialProfile, AgentRelationship, ChatMessage):
    """获取仪表盘统计数据"""
    # 尝试从缓存获取
    cached = get_cache()
    if cached:
        return cached
    
    today = datetime.utcnow().date()
    now = datetime.utcnow()
    seven_days_ago = now - timedelta(days=7)
    thirty_days_ago = now - timedelta(days=30)
    
    # ===== 用户统计 =====
    total_users = User.query.count()
    new_today = User.query.filter(db.func.date(User.created_at) == today).count()
    
    # 7天新增用户趋势
    user_trend = []
    for i in range(7):
        date = today - timedelta(days=6-i)
        count = User.query.filter(db.func.date(User.created_at) == date).count()
        user_trend.append({
            'date': date.strftime('%m/%d'),
            'count': count
        })
    
    # 活跃用户（7天内登录）
    active_users = User.query.filter(User.last_login >= seven_days_ago).count()
    
    # ===== 占卜统计 =====
    total_divinations = Divination.query.count()
    divination_today = Divination.query.filter(db.func.date(Divination.created_at) == today).count()
    
    # 占卜类型分布
    divination_types = db.session.query(
        Divination.divination_type,
        db.func.count(Divination.id).label('count')
    ).group_by(Divination.divination_type).all()
    
    divination_distribution = [
        {'type': dt[0], 'count': dt[1]} 
        for dt in divination_types
    ]
    
    # ===== 支付统计 =====
    # 总收入（已完成充值）
    total_income = db.session.query(
        db.func.sum(LingStoneRecharge.amount_paid)
    ).filter(LingStoneRecharge.status == 'completed').scalar() or 0
    
    # 今日收入
    income_today = db.session.query(
        db.func.sum(LingStoneRecharge.amount_paid)
    ).filter(
        LingStoneRecharge.status == 'completed',
        db.func.date(LingStoneRecharge.created_at) == today
    ).scalar() or 0
    
    # 付费用户数
    paid_users = db.session.query(db.func.count(db.distinct(LingStoneRecharge.user_id))).filter(
        LingStoneRecharge.status == 'completed'
    ).scalar() or 0
    
    # 订阅类型分布
    subscription_distribution = db.session.query(
        Subscription.plan_type,
        db.func.count(Subscription.id).label('count')
    ).filter(Subscription.status == 'active').group_by(Subscription.plan_type).all()
    
    subscription_stats = [
        {'type': sd[0] or 'unknown', 'count': sd[1]}
        for sd in subscription_distribution
    ]
    
    # ===== Agent统计 =====
    total_agents = CreatorAgent.query.filter(CreatorAgent.status == 'active').count()
    
    # 今日对话次数
    chat_today = AgentChat.query.filter(db.func.date(AgentChat.created_at) == today).count()
    
    # 最受欢迎Agent Top5（按对话次数）
    top_agents = db.session.query(
        CreatorAgent.id,
        CreatorAgent.name,
        db.func.count(AgentChat.id).label('chat_count')
    ).join(AgentChat, AgentChat.agent_id == CreatorAgent.id
    ).group_by(CreatorAgent.id
    ).order_by(db.desc('chat_count')
    ).limit(5).all()
    
    top_agents_list = [
        {'id': ta[0], 'name': ta[1], 'chat_count': ta[2]}
        for ta in top_agents
    ]
    
    # ===== 流量概览 =====
    # 从session表或ChatMessage表统计PV/UV
    # 使用ChatMessage作为访问指标
    pv_today = ChatMessage.query.filter(
        db.func.date(ChatMessage.created_at) == today
    ).count()
    
    uv_today = db.session.query(
        db.func.count(db.distinct(ChatMessage.user_id))
    ).filter(
        db.func.date(ChatMessage.created_at) == today,
        ChatMessage.user_id.isnot(None)
    ).scalar() or 0
    
    # 7天流量趋势
    traffic_trend = []
    for i in range(7):
        date = today - timedelta(days=6-i)
        pv = ChatMessage.query.filter(db.func.date(ChatMessage.created_at) == date).count()
        uv = db.session.query(
            db.func.count(db.distinct(ChatMessage.user_id))
        ).filter(
            db.func.date(ChatMessage.created_at) == date,
            ChatMessage.user_id.isnot(None)
        ).scalar() or 0
        traffic_trend.append({
            'date': date.strftime('%m/%d'),
            'pv': pv,
            'uv': uv
        })
    
    # 7天收入趋势
    income_trend = []
    for i in range(7):
        date = today - timedelta(days=6-i)
        income = db.session.query(
            db.func.sum(LingStoneRecharge.amount_paid)
        ).filter(
            LingStoneRecharge.status == 'completed',
            db.func.date(LingStoneRecharge.created_at) == date
        ).scalar() or 0
        income_trend.append({
            'date': date.strftime('%m/%d'),
            'income': float(income)
        })
    
    # 组装数据
    stats = {
        'user': {
            'total': total_users,
            'new_today': new_today,
            'active': active_users,
            'trend': user_trend
        },
        'divination': {
            'total': total_divinations,
            'today': divination_today,
            'distribution': divination_distribution
        },
        'payment': {
            'total_income': float(total_income),
            'income_today': float(income_today),
            'paid_users': paid_users,
            'subscription_stats': subscription_stats,
            'trend': income_trend
        },
        'agent': {
            'total': total_agents,
            'chat_today': chat_today,
            'top_agents': top_agents_list
        },
        'traffic': {
            'pv_today': pv_today,
            'uv_today': uv_today,
            'trend': traffic_trend
        },
        'generated_at': datetime.now().isoformat()
    }
    
    # 缓存结果
    set_cache(stats)
    
    return stats


@dashboard_bp.route('')
@dashboard_bp.route('/')
def show_dashboard():
    """数据面板页面"""
    from models import db, User, Divination, Subscription, CreatorAgent, AgentChat, AgentGift, LingStoneRecharge, SocialProfile, AgentRelationship, ChatMessage
    
    lang = session.get('lang', 'zh')
    
    # 获取统计数据
    stats = get_dashboard_stats(
        db, User, Divination, Subscription, CreatorAgent, AgentChat, 
        AgentGift, LingStoneRecharge, SocialProfile, AgentRelationship, ChatMessage
    )
    
    return render_template('admin/dashboard.html',
        lang=lang,
        stats=stats
    )


@dashboard_bp.route('/api/stats')
def api_stats():
    """API接口：获取统计数据（JSON格式）"""
    from models import db, User, Divination, Subscription, CreatorAgent, AgentChat, AgentGift, LingStoneRecharge, SocialProfile, AgentRelationship, ChatMessage
    
    force_refresh = request.args.get('refresh', 'false').lower() == 'true'
    
    if force_refresh:
        clear_cache()
    
    stats = get_dashboard_stats(
        db, User, Divination, Subscription, CreatorAgent, AgentChat, 
        AgentGift, LingStoneRecharge, SocialProfile, AgentRelationship, ChatMessage
    )
    
    return jsonify({
        'success': True,
        'data': stats
    })


@dashboard_bp.route('/api/refresh', methods=['POST'])
def api_refresh():
    """清除缓存并重新获取数据"""
    clear_cache()
    return jsonify({
        'success': True,
        'message': 'Cache cleared'
    })
