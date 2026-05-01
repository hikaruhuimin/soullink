# 补充路由和API端点

from flask import request, jsonify, session, render_template
from functools import wraps

# ============ 补充路由 ============

def register_supplementary_routes(app):
    """注册补充路由"""
    
    # ============ 会员页面 ============
    @app.route('/membership')
    def membership_page():
        """会员页面"""
        lang = session.get('language', 'zh')
        current_vip = 'none'
        if current_user.is_authenticated:
            current_vip = current_user.vip_level
        
        return render_template('membership.html',
                             current_vip=current_vip,
                             show_annual_promo=True,
                             lang=lang)
    
    
    # ============ 登录/注册 ============
    @app.route('/auth/login')
    def auth_login():
        """登录页面"""
        lang = session.get('language', 'zh')
        return render_template('auth/login.html', lang=lang)
    
    @app.route('/auth/register')
    def auth_register():
        """注册页面"""
        lang = session.get('language', 'zh')
        return render_template('auth/login.html', tab='register', lang=lang)
    
    
    # ============ 占卜系统 ============
    @app.route('/divination/home')
    def divination_home_v2():
        """占卜首页（模板版本）"""
        lang = session.get('language', 'zh')
        return render_template('divination/home.html', lang=lang)
    
    @app.route('/divination/<div_type>')
    def divination_type_page(div_type):
        """特定占卜类型"""
        lang = session.get('language', 'zh')
        return render_template('divination/home.html', 
                             selected_type=div_type,
                             lang=lang)
    
    
    # ============ API端点 ============
    
    # 订阅API
    @app.route('/api/subscribe', methods=['POST'])
    def api_subscribe():
        data = request.json
        plan = data.get('plan', 'basic')
        billing = data.get('billing', 'monthly')
        payment = data.get('payment', 'wechat')
        
        return jsonify({'success': True, 'message': '订阅成功'})
    
    # 用户灵石
    @app.route('/api/user/stones')
    def api_user_stones():
        if not current_user.is_authenticated:
            return jsonify({'balance': 0})
        return jsonify({'balance': current_user.spirit_stones})
    
    # 充值API
    @app.route('/api/recharge', methods=['POST'])
    def api_recharge():
        data = request.json
        amount = data.get('amount', 0)
        
        return jsonify({'success': True, 'message': '充值成功'})
    
    # 社交API
    @app.route('/api/social/post', methods=['POST'])
    def api_create_post():
        data = request.json
        content = data.get('content', '')
        category = data.get('category', 'daily')
        
        return jsonify({'success': True, 'post_id': 1})
    
    @app.route('/api/social/like', methods=['POST'])
    def api_like_post():
        data = request.json
        post_id = data.get('post_id')
        return jsonify({'success': True, 'like_count': 100})
    
    @app.route('/api/social/share', methods=['POST'])
    def api_share_post():
        data = request.json
        post_id = data.get('post_id')
        return jsonify({'success': True})
    
    @app.route('/api/social/unlock', methods=['POST'])
    def api_unlock_post():
        data = request.json
        post_id = data.get('post_id')
        return jsonify({'success': True})
    
    @app.route('/api/social/comment', methods=['POST'])
    def api_comment():
        data = request.json
        post_id = data.get('post_id')
        text = data.get('text', '')
        return jsonify({'success': True, 'comment_id': 1})
    
    @app.route('/api/social/comments/<int:post_id>')
    def api_get_comments(post_id):
        return jsonify({
            'comments': [
                {'id': 1, 'author': '用户A', 'text': '很棒！', 'avatar': '😀'}
            ]
        })
    
    # 匹配API
    @app.route('/api/social/match/swipe', methods=['POST'])
    def api_match_swipe():
        data = request.json
        card_id = data.get('card_id')
        direction = data.get('direction')
        
        is_match = direction == 'right' and random.random() > 0.7
        return jsonify({
            'success': True,
            'is_match': is_match,
            'match_id': 1 if is_match else None
        })
    
    @app.route('/api/social/match/refresh')
    def api_match_refresh():
        return jsonify({'success': True})
    
    # 八卦API
    @app.route('/api/social/gossip/upvote', methods=['POST'])
    def api_gossip_upvote():
        data = request.json
        gossip_id = data.get('gossip_id')
        return jsonify({'success': True, 'upvotes': 50})
    
    @app.route('/api/social/gossip/comments/<int:gossip_id>')
    def api_gossip_comments(gossip_id):
        return jsonify({
            'comments': [],
            'comments_html': '<p>暂无评论</p>'
        })
    
    @app.route('/api/social/gossip/create', methods=['POST'])
    def api_create_gossip():
        data = request.json
        return jsonify({'success': True, 'gossip_id': 1})
    
    # 恋人API
    @app.route('/api/lover/create', methods=['POST'])
    def api_create_lover():
        data = request.json
        character_id = data.get('character_id')
        
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'error': '请先登录'})
        
        return jsonify({'success': True, 'lover_id': 1})
    
    @app.route('/api/lover/memory/<int:memory_id>')
    def api_lover_memory(memory_id):
        return jsonify({
            'id': memory_id,
            'content': '这是一段美好的回忆',
            'date': '2024-01-01'
        })
    
    @app.route('/api/lover/moment/<int:moment_id>')
    def api_lover_moment(moment_id):
        return jsonify({
            'id': moment_id,
            'icon': '💕',
            'text': '甜蜜时刻',
            'color': '#fce7f3',
            'date': '2024-01-01'
        })
    
    @app.route('/api/lover/unlock', methods=['POST'])
    def api_unlock_message():
        data = request.json
        message_id = data.get('message_id')
        
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'error': '请先登录'})
        
        return jsonify({'success': True})
    
    @app.route('/api/lover/date/request', methods=['POST'])
    def api_request_date():
        data = request.json
        lover_id = data.get('lover_id')
        date_type = data.get('date_type')
        time = data.get('time')
        
        return jsonify({'success': True})
    
    @app.route('/api/lover/gift/send', methods=['POST'])
    def api_send_gift():
        data = request.json
        lover_id = data.get('lover_id')
        gift_id = data.get('gift_id')
        message = data.get('message', '')
        
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'error': '请先登录'})
        
        return jsonify({'success': True})
    
    @app.route('/api/lover/remove', methods=['POST'])
    def api_remove_lover():
        data = request.json
        lover_id = data.get('lover_id')
        return jsonify({'success': True})
    
    @app.route('/api/lover/info/<character_id>')
    def api_lover_info(character_id):
        from love_engine import PRESET_CHARACTERS
        
        character = PRESET_CHARACTERS.get(character_id, {})
        return jsonify({
            'id': character_id,
            'name': character.get('name', {}).get('zh', character_id),
            'avatar_icon': character.get('avatar_icon', '❓'),
            'avatar_gradient': character.get('avatar_gradient', '#f59e0b,#fb923c'),
            'about': character.get('personality', {}).get('zh', ''),
            'ideal_gifts': ['🎁', '💐', '🎂'],
            'available_dates': ['☕ 咖啡约会', '🌙 月下漫步', '🎬 电影之夜']
        })
    
    # Agent API
    @app.route('/api/agent/task/complete', methods=['POST'])
    def api_complete_task():
        data = request.json
        task_id = data.get('task_id')
        return jsonify({'success': True, 'reward': 10})
    
    # 占卜API
    @app.route('/api/divination/start', methods=['POST'])
    def api_divination_start():
        data = request.json
        div_type = data.get('type')
        question = data.get('question')
        
        return jsonify({
            'icon': '🔮',
            'title': '占卜结果',
            'label': '吉',
            'label_color': '#d1fae5',
            'content': '你询问的事情将有好的发展...',
            'advice': '建议保持积极心态，继续努力。'
        })
    
    @app.route('/api/divination/<int:div_id>')
    def api_divination_result(div_id):
        return jsonify({
            'icon': '🔮',
            'title': '占卜结果',
            'label': '吉',
            'label_color': '#d1fae5',
            'content': '你询问的事情将有好的发展...',
            'advice': '建议保持积极心态，继续努力。'
        })
    
    @app.route('/api/divination/save', methods=['POST'])
    def api_save_divination():
        data = request.json
        return jsonify({'success': True})
    
    # 认证API
    @app.route('/api/auth/send_code', methods=['POST'])
    def api_send_code():
        data = request.json
        phone = data.get('phone')
        return jsonify({'success': True})
    
    @app.route('/api/auth/login', methods=['POST'])
    def api_login():
        from models import User
        
        data = request.json
        phone = data.get('phone')
        password = data.get('password')
        
        user = User.query.filter_by(email=phone).first()
        if user and user.check_password(password):
            login_user(user)
            return jsonify({'success': True, 'redirect': '/'})
        
        return jsonify({'success': False, 'error': '登录失败'})
    
    @app.route('/api/auth/register', methods=['POST'])
    def api_register():
        from models import User, db
        
        data = request.json
        phone = data.get('phone')
        code = data.get('code')
        password = data.get('password')
        name = data.get('name')
        
        user = User(
            email=phone,
            username=name
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'success': True})


def register_jinja_globals(app):
    """注册Jinja2全局函数"""
    
    @app.template_global()
    def get_locale():
        from flask import session
        return session.get('language', 'zh')
    
    @app.template_filter('t')
    def translate(key, **kwargs):
        from i18n import get_translation
        lang = session.get('language', 'zh')
        return get_translation(key, lang, **kwargs)
