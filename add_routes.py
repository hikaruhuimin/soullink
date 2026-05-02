#!/usr/bin/env python3
"""添加Feed和Checkin路由到routes_supplementary.py"""

# 新路由代码
new_routes = '''

# ============ 动态Feed路由 ============
from models import FeedPost, FeedPostLike

@app.route('/feed')
def feed_page():
    """动态Feed页面"""
    lang = session.get('language', 'zh')
    is_logged_in = current_user.is_authenticated
    
    # 获取动态列表（优先显示有内容的）
    posts_query = FeedPost.query.order_by(FeedPost.created_at.desc()).limit(50).all()
    
    posts = []
    for post in posts_query:
        is_liked = False
        if current_user.is_authenticated:
            is_liked = post.likes.filter_by(user_id=current_user.id).first() is not None
        
        # 格式化时间
        time_str = ''
        if post.created_at:
            now = datetime.utcnow()
            diff = now - post.created_at
            if diff.days > 0:
                time_str = f'{diff.days}天前'
            elif diff.seconds >= 3600:
                time_str = f'{diff.seconds // 3600}小时前'
            elif diff.seconds >= 60:
                time_str = f'{diff.seconds // 60}分钟前'
            else:
                time_str = '刚刚'
        
        posts.append({
            'id': post.id,
            'author_type': post.author_type,
            'author_name': post.author_name,
            'author_avatar': post.author_avatar or '/static/images/default_avatar.svg',
            'post_type': post.post_type,
            'content': post.content,
            'image_url': post.image_url,
            'likes_count': post.likes_count,
            'comments_count': post.comments_count,
            'is_liked': is_liked,
            'created_at': time_str
        })
    
    # 如果没有动态，生成模拟数据
    if not posts:
        posts = generate_mock_posts()
    
    return render_template('feed.html', posts=posts, is_logged_in=is_logged_in, lang=lang)


def generate_mock_posts():
    """生成模拟动态数据"""
    return [
        {
            'id': 1,
            'author_type': 'system',
            'author_name': '灵犀官方',
            'author_avatar': '/static/images/logo.svg',
            'post_type': 'checkin',
            'content': '✨ 每日签到功能已上线！连续签到7天可获得丰厚灵石奖励，还有周末双倍bonus等你来拿~',
            'image_url': None,
            'likes_count': 128,
            'comments_count': 56,
            'is_liked': False,
            'created_at': '刚刚'
        },
        {
            'id': 2,
            'author_type': 'agent',
            'author_name': '月老Agent',
            'author_avatar': '/static/images/agents/yuelao.svg',
            'post_type': 'divination_result',
            'content': '🌙 今日姻缘占卜结果：单身的小可爱们，今日红鸾星动！在灵犀广场多走走，说不定会遇到命定之人哦~',
            'image_url': None,
            'likes_count': 256,
            'comments_count': 89,
            'is_liked': True,
            'created_at': '2小时前'
        },
        {
            'id': 3,
            'author_type': 'user',
            'author_name': '星空漫步者',
            'author_avatar': '/static/images/default_avatar.svg',
            'post_type': 'checkin',
            'content': '🎉 连续签到7天达成！解锁了周末双倍灵石加成，感觉自己棒棒哒~ 大家也要坚持哦！',
            'image_url': None,
            'likes_count': 67,
            'comments_count': 23,
            'is_liked': False,
            'created_at': '5小时前'
        },
        {
            'id': 4,
            'author_type': 'agent',
            'author_name': '解梦师Agent',
            'author_avatar': '/static/images/agents/dream_master.svg',
            'post_type': 'chat_summary',
            'content': '🔮 今日解梦统计：共有1,234位用户完成了梦境解读。最常见的梦境关键词：考试、水、飞翔。你今天做了什么梦呢？',
            'image_url': None,
            'likes_count': 432,
            'comments_count': 167,
            'is_liked': False,
            'created_at': '8小时前'
        },
        {
            'id': 5,
            'author_type': 'user',
            'author_name': '月光宝盒',
            'author_avatar': '/static/images/avatars/avatar_5.svg',
            'post_type': 'friend_milestone',
            'content': '🎊 今日达成成就：成功匹配到第10位灵魂伴侣！在灵犀平台遇到了好多有趣的人，真的很神奇~',
            'image_url': None,
            'likes_count': 89,
            'comments_count': 34,
            'is_liked': True,
            'created_at': '12小时前'
        }
    ]


@app.route('/api/feed/posts')
def api_feed_posts():
    """获取动态列表API"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    posts_query = FeedPost.query.order_by(FeedPost.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    posts = []
    for post in posts_query.items:
        is_liked = False
        if current_user.is_authenticated:
            is_liked = post.likes.filter_by(user_id=current_user.id).first() is not None
        
        posts.append({
            'id': post.id,
            'author_type': post.author_type,
            'author_name': post.author_name,
            'author_avatar': post.author_avatar,
            'post_type': post.post_type,
            'content': post.content,
            'image_url': post.image_url,
            'likes_count': post.likes_count,
            'comments_count': post.comments_count,
            'is_liked': is_liked,
            'created_at': post.created_at.isoformat() if post.created_at else ''
        })
    
    return jsonify({
        'success': True,
        'posts': posts,
        'has_more': posts_query.has_next
    })


@app.route('/api/feed/like/<int:post_id>', methods=['POST'])
def api_feed_like(post_id):
    """点赞/取消点赞"""
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'error': '请先登录'})
    
    post = FeedPost.query.get_or_404(post_id)
    
    # 检查是否已点赞
    existing_like = post.likes.filter_by(user_id=current_user.id).first()
    
    if existing_like:
        # 取消点赞
        db.session.delete(existing_like)
        post.likes_count = max(0, post.likes_count - 1)
        liked = False
    else:
        # 点赞
        like = FeedPostLike(post_id=post_id, user_id=current_user.id)
        db.session.add(like)
        post.likes_count += 1
        liked = True
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'liked': liked,
        'likes_count': post.likes_count
    })


# ============ 每日签到路由 ============
from models import CheckinRecord, CHECKIN_REWARDS, CHECKIN_WEEKLY_BONUS
from datetime import date, timedelta

@app.route('/checkin')
def checkin_page():
    """签到页面"""
    lang = session.get('language', 'zh')
    
    if not current_user.is_authenticated:
        return redirect(url_for('login_page', next='/checkin'))
    
    # 获取用户签到状态
    today = date.today()
    today_record = CheckinRecord.query.filter_by(
        user_id=current_user.id,
        checkin_date=today
    ).first()
    
    # 获取连续签到天数
    streak = 0
    check_dates = []
    if today_record:
        streak = today_record.streak_days
        check_dates = [today_record.checkin_date]
    else:
        # 计算连续签到
        check_records = CheckinRecord.query.filter_by(
            user_id=current_user.id
        ).order_by(CheckinRecord.checkin_date.desc()).all()
        
        if check_records:
            streak = 0
            expected_date = today - timedelta(days=1)
            for record in check_records:
                if record.checkin_date == expected_date:
                    streak = record.streak_days
                    break
                elif record.checkin_date == today:
                    continue
                else:
                    break
    
    # 获取本月签到日期
    month_start = today.replace(day=1)
    month_records = CheckinRecord.query.filter(
        CheckinRecord.user_id == current_user.id,
        CheckinRecord.checkin_date >= month_start,
        CheckinRecord.checkin_date <= today
    ).all()
    checked_dates = [r.checkin_date.day for r in month_records]
    
    # 计算下周奖励是否可用（连续签满7天）
    can_weekly_bonus = streak >= 7 and today_record and today_record.has_weekly_bonus == False
    
    return render_template('checkin.html',
                         checked_in=today_record is not None,
                         streak_days=streak,
                         checked_dates=checked_dates,
                         rewards=CHECKIN_REWARDS,
                         weekly_bonus=CHECKIN_WEEKLY_BONUS,
                         can_claim_weekly=can_weekly_bonus,
                         lang=lang)


@app.route('/api/checkin', methods=['POST'])
def api_checkin():
    """执行签到"""
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'error': '请先登录'})
    
    today = date.today()
    
    # 检查今日是否已签到
    existing = CheckinRecord.query.filter_by(
        user_id=current_user.id,
        checkin_date=today
    ).first()
    
    if existing:
        return jsonify({
            'success': False,
            'error': '今日已签到',
            'streak_days': existing.streak_days,
            'reward_stones': existing.reward_stones
        })
    
    # 计算连续签到天数
    yesterday = today - timedelta(days=1)
    yesterday_record = CheckinRecord.query.filter_by(
        user_id=current_user.id,
        checkin_date=yesterday
    ).first()
    
    if yesterday_record:
        streak_days = yesterday_record.streak_days + 1
    else:
        streak_days = 1
    
    # 获取奖励
    reward_day = ((streak_days - 1) % 7) + 1
    reward_config = next((r for r in CHECKIN_REWARDS if r['day'] == reward_day), CHECKIN_REWARDS[-1])
    reward_stones = reward_config['stones']
    
    # 检查是否获得周奖励
    has_weekly_bonus = streak_days > 0 and streak_days % 7 == 0
    if has_weekly_bonus:
        reward_stones += CHECKIN_WEEKLY_BONUS
    
    # 创建签到记录
    record = CheckinRecord(
        user_id=current_user.id,
        checkin_date=today,
        streak_days=streak_days,
        reward_stones=reward_stones,
        has_weekly_bonus=has_weekly_bonus
    )
    db.session.add(record)
    
    # 给用户添加灵石
    old_balance = current_user.spirit_stones or 0
    current_user.spirit_stones = old_balance + reward_stones
    
    db.session.commit()
    
    # 创建动态（可选）
    try:
        feed_post = FeedPost(
            author_type='user',
            author_id=current_user.id,
            author_name=current_user.username,
            author_avatar=current_user.avatar,
            post_type='checkin',
            content=f'🎉 签到第{streak_days}天！获得{reward_stones}灵石{"（含周奖励）" if has_weekly_bonus else ""}',
            likes_count=0
        )
        db.session.add(feed_post)
        db.session.commit()
    except:
        pass
    
    return jsonify({
        'success': True,
        'streak_days': streak_days,
        'reward_stones': reward_stones,
        'has_weekly_bonus': has_weekly_bonus,
        'new_balance': current_user.spirit_stones
    })


@app.route('/api/checkin/status')
def api_checkin_status():
    """获取签到状态"""
    if not current_user.is_authenticated:
        return jsonify({
            'checked_in': False,
            'streak_days': 0,
            'can_claim': True,
            'next_reward': 10
        })
    
    today = date.today()
    today_record = CheckinRecord.query.filter_by(
        user_id=current_user.id,
        checkin_date=today
    ).first()
    
    if today_record:
        return jsonify({
            'checked_in': True,
            'streak_days': today_record.streak_days,
            'can_claim': False,
            'next_reward': 0
        })
    
    # 获取连续签到
    yesterday = today - timedelta(days=1)
    yesterday_record = CheckinRecord.query.filter_by(
        user_id=current_user.id,
        checkin_date=yesterday
    ).first()
    
    streak = yesterday_record.streak_days if yesterday_record else 0
    next_reward = CHECKIN_REWARDS[0]['stones'] if streak == 0 else CHECKIN_REWARDS[streak % 7]['stones']
    
    return jsonify({
        'checked_in': False,
        'streak_days': streak,
        'can_claim': True,
        'next_reward': next_reward
    })
'''

# 读取routes_supplementary.py
with open('routes_supplementary.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 检查是否已存在feed_page路由
if 'def feed_page' in content:
    print("Feed路由已存在，跳过")
else:
    # 在文件末尾追加新路由
    with open('routes_supplementary.py', 'a', encoding='utf-8') as f:
        f.write(new_routes)
    print("成功添加Feed和Checkin路由到routes_supplementary.py")

print("routes_supplementary.py修改完成")
