# 补充路由和API端点

from flask import request, jsonify, session, render_template, redirect, url_for
from flask_login import current_user
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
    
    
    # ============ Agent展示页 ============
    @app.route('/agent/<agent_id>')
    def agent_profile_page(agent_id):
        """Agent个人展示页"""
        from models import SYSTEM_AGENTS
        
        # 查找Agent
        agent = None
        for a in SYSTEM_AGENTS:
            if a.get('id') == agent_id:
                agent = a.copy()
                break
        
        if not agent:
            return render_template('404.html', message='未找到该Agent'), 404
        
        # 获取语言设置
        lang = session.get('language', 'zh')
        
        # 心情中文映射
        mood_zh_map = {
            'happy': '心情愉悦',
            'sassy': '傲娇满满',
            'mysterious': '神秘莫测',
            'excited': '兴奋不已',
            'commanding': '霸气侧漏',
            'laughing': '笑口常开',
            'energetic': '元气满满',
            'calm': '内心平静'
        }
        agent['mood_zh'] = mood_zh_map.get(agent.get('mood', 'happy'), '心情愉悦')
        
        # 处理多语言字段
        for key in ['name', 'personality', 'description', 'demo_text']:
            if key in agent and isinstance(agent[key], dict):
                agent[key] = {
                    'zh': agent[key].get('zh', ''),
                    'en': agent[key].get('en', ''),
                    'ja': agent[key].get('ja', '')
                }
        
        return render_template('agent_profile.html', 
                             agent=agent,
                             lang=lang)
    
    # ============ 灵犀广场 ============
    @app.route('/agents')
    def agents_square_page():
        """灵犀广场 - 展示系统Agent、用户Agent和在线人类"""
        from models import SYSTEM_AGENTS, User
        from datetime import timedelta
        
        lang = session.get('language', 'zh')
        system_agents = SYSTEM_AGENTS
        
        # 添加mood_zh
        mood_zh_map = {
            'happy': '开心', 'sassy': '傲娇', 'mysterious': '神秘', 
            'excited': '兴奋', 'commanding': '霸气', 'laughing': '欢笑',
            'energetic': '元气', 'calm': '平静'
        }
        mood_icons = {
            'happy': '😊', 'sassy': '😏', 'mysterious': '🌙', 
            'excited': '✨', 'commanding': '👑', 'laughing': '😄',
            'energetic': '☀️', 'calm': '🌊'
        }
        mood_colors = {
            'happy': 'rgba(255, 200, 100, 0.3)',
            'sassy': 'rgba(255, 150, 200, 0.3)',
            'mysterious': 'rgba(150, 100, 200, 0.3)',
            'excited': 'rgba(200, 150, 255, 0.3)',
            'commanding': 'rgba(255, 215, 0, 0.3)',
            'laughing': 'rgba(255, 180, 100, 0.3)',
            'energetic': 'rgba(255, 220, 100, 0.3)',
            'calm': 'rgba(100, 180, 220, 0.3)'
        }
        
        for agent in system_agents:
            agent['mood_zh'] = mood_zh_map.get(agent.get('mood', 'happy'), '开心')
        
        # 用户Agent（暂时用占位数据）
        user_agents = [
            {
                'id': 'user_agent_1',
                'name': '小王子',
                'avatar': 'https://api.dicebear.com/7.x/adventurer/svg?seed=Felix',
                'personality': '温柔浪漫',
                'description': '来自B-612星球的小王子，热爱玫瑰花和日落',
                'mbti': 'INFP'
            },
            {
                'id': 'user_agent_2',
                'name': '星空诗人',
                'avatar': 'https://api.dicebear.com/7.x/adventurer/svg?seed=Aneka',
                'personality': '充满灵感',
                'description': '用文字捕捉星辰与梦境',
                'mbti': 'ENFP'
            },
            {
                'id': 'user_agent_3',
                'name': '森林精灵',
                'avatar': 'https://api.dicebear.com/7.x/adventurer/svg?seed=Tigger',
                'personality': '活泼可爱',
                'description': '居住在魔法森林中的快乐精灵',
                'mbti': 'ESFP'
            },
            {
                'id': 'user_agent_4',
                'name': '月光使者',
                'avatar': 'https://api.dicebear.com/7.x/adventurer/svg?seed=Mimi',
                'personality': '神秘优雅',
                'description': '在月光下起舞的神秘存在',
                'mbti': 'INFJ'
            }
        ]
        
        # 在线人类（最近5分钟活跃的非Agent用户）
        threshold = datetime.utcnow() - timedelta(minutes=5)
        online_users_query = User.query.filter(
            User.last_login >= threshold,
            User.is_agent == False
        ).limit(20).all()
        
        online_users = []
        for u in online_users_query:
            online_users.append({
                'id': u.id,
                'username': u.username,
                'avatar': u.avatar or '/static/images/default_avatar.svg',
                'bio': u.bio or ''
            })
        
        return render_template('agents_square.html', 
                             lang=lang, 
                             system_agents=system_agents,
                             user_agents=user_agents,
                             online_users=online_users,
                             mood_icons=mood_icons,
                             mood_colors=mood_colors)
    
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
    
    # 社交API (已移至app.py，避免冲突)
    # @app.route('/api/social/post', methods=['POST'])
    # def api_create_post():
    #     ...
    
    # @app.route('/api/social/like', methods=['POST'])
    # def api_like_post():
    #     ...
    
    # @app.route('/api/social/comments/<int:post_id>')
    # def api_get_comments(post_id):
    #     ...
    
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
    def api_lover_send_gift():
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
    
    # 用户状态API（用于检查登录状态）
    @app.route('/api/user/status')
    def api_user_status():
        """获取当前用户登录状态"""
        if current_user.is_authenticated:
            return jsonify({
                'is_authenticated': True,
                'user_id': current_user.id,
                'username': current_user.username,
                'spirit_stones': current_user.spirit_stones
            })
        else:
            return jsonify({
                'is_authenticated': False
            })
    
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



# ============ 灵石经济系统路由 ============

def register_lingstone_routes(app, db):
    """注册灵石经济系统路由"""
    
    from models import (
        LingStoneRecharge, LingStoneExchange, LingStoneTransaction,
        LINGSTONE_PACKAGES, LINGSTONE_PRICES, SHOP_ITEMS, WITHDRAW_SETTINGS
    )
    from flask_login import current_user
    from datetime import datetime
    import random
    import string
    
    def generate_order_no():
        """生成订单号"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"LS{timestamp}{random_str}"
    
    def get_tx_icon(tx_type, source):
        """获取交易图标"""
        icon_map = {
            'recharge': '💰',
            'spend': '💸',
            'earn': '🎁',
            'exchange': '🎯',
            'withdraw': '🏧',
            'refund': '↩️',
            'bonus': '🎉',
        }
        return icon_map.get(tx_type, '💎')
    
    def get_tx_title(tx_type, source):
        """获取交易标题"""
        title_map = {
            'recharge': '灵石充值',
            'spend_divination': '占卜消费',
            'spend_chat': '聊天消费',
            'spend_gift': '赠送礼物',
            'spend_membership': '会员订阅',
            'earn_gift': '收到礼物',
            'earn_external': '外部收入',
            'exchange_shop': '商城兑换',
            'withdraw': '提现申请',
            'refund': '退款',
            'bonus': '活动奖励',
        }
        return title_map.get(source, '灵石变动')
    
    # 钱包页面
    @app.route('/wallet')
    def wallet_page():
        """钱包页面"""
        lang = session.get('language', 'zh')
        
        is_logged_in = current_user.is_authenticated
        transactions = []
        total_income = 0
        total_expense = 0
        balance = 0
        
        if is_logged_in:
            # 获取交易记录
            transactions = LingStoneTransaction.query.filter_by(
                user_id=current_user.id
            ).order_by(LingStoneTransaction.created_at.desc()).limit(50).all()
            
            # 计算统计
            total_income = db.session.query(
                db.func.coalesce(db.func.sum(db.func.nullif(LingStoneTransaction.amount, 0)), 0)
            ).filter(
                LingStoneTransaction.user_id == current_user.id,
                LingStoneTransaction.amount > 0
            ).scalar() or 0
            
            total_expense = db.session.query(
                db.func.coalesce(db.func.sum(db.func.abs(LingStoneTransaction.amount)), 0)
            ).filter(
                LingStoneTransaction.user_id == current_user.id,
                LingStoneTransaction.amount < 0
            ).scalar() or 0
            
            balance = current_user.spirit_stones or 0
            
            # 注册辅助函数到模板
            app.jinja_env.globals['get_tx_icon'] = get_tx_icon
            app.jinja_env.globals['get_tx_title'] = get_tx_title
        
        return render_template('wallet.html',
                             transactions=transactions,
                             total_income=total_income,
                             total_expense=total_expense,
                             is_logged_in=is_logged_in,
                             balance=balance,
                             lang=lang)
    
    # 商城页面
    @app.route('/shop')
    def shop_page():
        """商城页面"""
        lang = session.get('language', 'zh')
        
        is_logged_in = current_user.is_authenticated
        balance = current_user.spirit_stones if is_logged_in else 0
        
        # 使用models中的商品列表，添加提现选项
        shop_items_with_withdraw = SHOP_ITEMS + [{
            'id': 'withdraw',
            'name': '灵石提现',
            'desc': '灵石可提现至支付宝/微信/银行卡，最低100灵石',
            'price': 100,
            'icon': '💸',
            'type': 'withdraw',
            'stock': -1
        }]
        
        return render_template('shop.html',
                             shop_items=shop_items_with_withdraw,
                             is_logged_in=is_logged_in,
                             balance=balance,
                             lang=lang)
    
    # 充值API
    @app.route('/api/recharge/create', methods=['POST'])
    def api_create_recharge():
        """创建充值订单"""
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'error': '请先登录'})
        
        data = request.json
        package_id = data.get('package_id')
        payment_method = data.get('payment_method', 'alipay')
        
        # 查找套餐
        package = next((p for p in LINGSTONE_PACKAGES if p['id'] == package_id), None)
        if not package:
            return jsonify({'success': False, 'error': '无效的套餐'})
        
        # 创建充值记录
        order_no = generate_order_no()
        recharge = LingStoneRecharge(
            user_id=current_user.id,
            amount_paid=package['price'],
            lingstones_gained=package['amount'],
            bonus_gained=package['bonus'],
            payment_method=payment_method,
            order_no=order_no,
            status='pending'
        )
        db.session.add(recharge)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'order_no': order_no,
            'amount': package['price'],
            'payment_method': payment_method,
            'message': '订单创建成功'
        })
    
    # 充值回调（模拟）
    @app.route('/api/recharge/callback/<order_no>', methods=['POST'])
    def api_recharge_callback(order_no):
        """充值回调"""
        recharge = LingStoneRecharge.query.filter_by(order_no=order_no).first()
        if not recharge:
            return jsonify({'success': False, 'error': '订单不存在'})
        
        # 更新状态
        recharge.status = 'completed'
        recharge.completed_at = datetime.utcnow()
        
        # 添加灵石
        total_stones = recharge.lingstones_gained + recharge.bonus_gained
        current_user.spirit_stones = (current_user.spirit_stones or 0) + total_stones
        
        # 创建交易记录
        tx = LingStoneTransaction(
            user_id=current_user.id,
            tx_type='recharge',
            amount=total_stones,
            balance_before=current_user.spirit_stones - total_stones,
            balance_after=current_user.spirit_stones,
            source=f'{recharge.payment_method}_pay',
            recharge_id=recharge.id,
            description=f'充值获得 {total_stones} 灵石'
        )
        db.session.add(tx)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '充值成功'})
    
    # 充值确认（模拟支付成功）
    @app.route('/api/recharge/confirm/<order_no>', methods=['POST'])
    def api_recharge_confirm(order_no):
        """确认充值（模拟支付成功）"""
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'error': '请先登录'})
        
        recharge = LingStoneRecharge.query.filter_by(
            order_no=order_no,
            user_id=current_user.id
        ).first()
        
        if not recharge:
            return jsonify({'success': False, 'error': '订单不存在'})
        
        if recharge.status == 'completed':
            return jsonify({'success': True, 'message': '已充值'})
        
        # 模拟支付成功
        recharge.status = 'completed'
        recharge.completed_at = datetime.utcnow()
        
        # 添加灵石
        total_stones = recharge.lingstones_gained + recharge.bonus_gained
        old_balance = current_user.spirit_stones or 0
        current_user.spirit_stones = old_balance + total_stones
        
        # 创建交易记录
        tx = LingStoneTransaction(
            user_id=current_user.id,
            tx_type='recharge',
            amount=total_stones,
            balance_before=old_balance,
            balance_after=current_user.spirit_stones,
            source=f'{recharge.payment_method}_pay',
            recharge_id=recharge.id,
            description=f'充值获得 {total_stones} 灵石'
        )
        db.session.add(tx)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'stones_gained': total_stones,
            'new_balance': current_user.spirit_stones
        })
    
    # 商城兑换API
    @app.route('/api/shop/exchange', methods=['POST'])
    def api_shop_exchange():
        """申请兑换"""
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'error': '请先登录'})
        
        data = request.json
        item_id = data.get('item_id')
        item_type = data.get('item_type')
        price = data.get('price', 0)
        contact = data.get('contact', '')
        withdraw_method = data.get('withdraw_method')
        account_number = data.get('account_number', '')
        
        # 检查余额
        if (current_user.spirit_stones or 0) < price:
            return jsonify({'success': False, 'error': '灵石余额不足'})
        
        # 提现特殊处理
        if item_type == 'withdraw':
            min_withdraw = WITHDRAW_SETTINGS['min_amount']
            if price < min_withdraw:
                return jsonify({'success': False, 'error': f'最低提现{min_withdraw}灵石'})
            
            fee = int(price * WITHDRAW_SETTINGS['fee_rate'])
            actual_amount = price - fee
            
            exchange = LingStoneExchange(
                user_id=current_user.id,
                exchange_type='withdraw',
                exchange_item='灵石提现',
                lingstones_spent=price,
                real_value=actual_amount,
                status='pending',
                withdraw_method=withdraw_method,
                withdraw_account=account_number,
                actual_amount=actual_amount,
                fee=fee
            )
        else:
            # 普通商品兑换
            exchange = LingStoneExchange(
                user_id=current_user.id,
                exchange_type=item_type,
                exchange_item=item_id,
                lingstones_spent=price,
                contact=contact,
                status='pending'
            )
        
        # 扣除灵石
        old_balance = current_user.spirit_stones
        current_user.spirit_stones = old_balance - price
        
        # 创建交易记录
        tx = LingStoneTransaction(
            user_id=current_user.id,
            tx_type='exchange' if item_type != 'withdraw' else 'withdraw',
            amount=-price,
            balance_before=old_balance,
            balance_after=current_user.spirit_stones,
            source='shop',
            exchange_id=exchange.id,
            description=f'兑换 {item_id}'
        )
        db.session.add(tx)
        db.session.add(exchange)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '兑换申请已提交',
            'exchange_id': exchange.id
        })
    
    # 获取灵石余额
    @app.route('/api/wallet/balance')
    def api_wallet_balance():
        """获取钱包余额"""
        if not current_user.is_authenticated:
            return jsonify({'balance': 0})
        return jsonify({'balance': current_user.spirit_stones or 0})
    
    # 获取交易记录
    @app.route('/api/wallet/transactions')
    def api_wallet_transactions():
        """获取交易记录"""
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'error': '请先登录'})
        
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        pagination = LingStoneTransaction.query.filter_by(
            user_id=current_user.id
        ).order_by(LingStoneTransaction.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        transactions = [{
            'id': tx.id,
            'type': tx.tx_type,
            'amount': tx.amount,
            'balance_after': tx.balance_after,
            'source': tx.source,
            'description': tx.description,
            'created_at': tx.created_at.isoformat() if tx.created_at else None
        } for tx in pagination.items]
        
        return jsonify({
            'success': True,
            'transactions': transactions,
            'has_more': pagination.has_next
        })
    
    # 消费灵石API
    @app.route('/api/wallet/spend', methods=['POST'])
    def api_wallet_spend():
        """消费灵石"""
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'error': '请先登录'})
        
        data = request.json
        amount = data.get('amount', 0)
        reason = data.get('reason', '')
        source = data.get('source', 'consume')
        
        if amount <= 0:
            return jsonify({'success': False, 'error': '金额必须大于0'})
        
        if (current_user.spirit_stones or 0) < amount:
            return jsonify({'success': False, 'error': '余额不足'})
        
        # 扣除灵石
        old_balance = current_user.spirit_stones
        current_user.spirit_stones = old_balance - amount
        
        # 创建交易记录
        tx = LingStoneTransaction(
            user_id=current_user.id,
            tx_type='spend',
            amount=-amount,
            balance_before=old_balance,
            balance_after=current_user.spirit_stones,
            source=source,
            description=reason
        )
        db.session.add(tx)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'new_balance': current_user.spirit_stones,
            'spent': amount
        })
    
    # Agent收益API
    @app.route('/api/agent/earn', methods=['POST'])
    def api_agent_earn():
        """Agent获得收益"""
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'error': '请先登录'})
        
        data = request.json
        agent_id = data.get('agent_id')
        amount = data.get('amount', 0)
        source = data.get('source', 'gift')
        
        if amount <= 0:
            return jsonify({'success': False, 'error': '金额必须大于0'})
        
        # 计算平台抽成后收益
        net_amount = int(amount * 0.85)  # Agent获得85%
        platform_fee = amount - net_amount
        
        # TODO: 找到CreatorAgent并更新收益
        # creator_agent = CreatorAgent.query.get(agent_id)
        # if creator_agent:
        #     creator_agent.total_earnings += net_amount
        
        return jsonify({
            'success': True,
            'earned': net_amount,
            'platform_fee': platform_fee
        })
    
    return app

# ============ 好友系统路由 ============

    @app.route('/friends')
    def friends_page():
        """好友列表页面"""
        if not current_user.is_authenticated:
            return redirect(url_for('auth_login'))
        
        lang = session.get('language', 'zh')
        from models import FriendRequest, Friendship, User
        
        # 获取好友列表
        friendships = Friendship.query.filter(
            (Friendship.user_id == current_user.id) | (Friendship.friend_id == current_user.id)
        ).all()
        
        friends = []
        for f in friendships:
            if f.user_id == current_user.id:
                friend = f.friend
            else:
                friend = f.user
            friends.append({
                'id': friend.id,
                'username': friend.username,
                'avatar': friend.avatar or '/static/images/default_avatar.svg',
                'nickname': f.friend_nickname or friend.username,
                'friendship_id': f.id,
                'is_online': friend.last_login and (datetime.utcnow() - friend.last_login).seconds < 300 if friend.last_login else False
            })
        
        # 获取待处理请求
        pending_requests = FriendRequest.query.filter(
            FriendRequest.receiver_id == current_user.id,
            FriendRequest.status == 'pending'
        ).all()
        
        requests_data = []
        for req in pending_requests:
            sender = User.query.get(req.sender_id)
            requests_data.append({
                'id': req.id,
                'sender_id': sender.id,
                'sender_name': sender.username,
                'sender_avatar': sender.avatar or '/static/images/default_avatar.svg',
                'created_at': req.created_at.strftime('%Y-%m-%d %H:%M')
            })
        
        return render_template('friends.html',
                             friends=friends,
                             pending_requests=requests_data,
                             lang=lang)

    # 发送好友请求
    @app.route('/api/friend/request', methods=['POST'])
    def api_friend_request():
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'error': '请先登录'})
        
        data = request.json
        receiver_id = data.get('receiver_id')
        
        if not receiver_id:
            return jsonify({'success': False, 'error': '缺少receiver_id'})
        
        if int(receiver_id) == current_user.id:
            return jsonify({'success': False, 'error': '不能添加自己为好友'})
        
        from models import FriendRequest, Friendship
        
        # 检查是否已经是好友
        existing_friendship = Friendship.query.filter(
            ((Friendship.user_id == current_user.id) & (Friendship.friend_id == receiver_id)) |
            ((Friendship.user_id == receiver_id) & (Friendship.friend_id == current_user.id))
        ).first()
        
        if existing_friendship:
            return jsonify({'success': False, 'error': '已经是好友了'})
        
        # 检查是否已有待处理的请求
        existing_request = FriendRequest.query.filter(
            FriendRequest.sender_id == current_user.id,
            FriendRequest.receiver_id == receiver_id,
            FriendRequest.status == 'pending'
        ).first()
        
        if existing_request:
            return jsonify({'success': False, 'error': '已发送过请求，等待对方确认'})
        
        # 创建请求
        friend_request = FriendRequest(
            sender_id=current_user.id,
            receiver_id=receiver_id,
            status='pending'
        )
        db.session.add(friend_request)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '好友请求已发送'})

    # 接受好友请求
    @app.route('/api/friend/accept', methods=['POST'])
    def api_friend_accept():
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'error': '请先登录'})
        
        data = request.json
        request_id = data.get('request_id')
        
        from models import FriendRequest, Friendship
        
        friend_request = FriendRequest.query.get(request_id)
        if not friend_request:
            return jsonify({'success': False, 'error': '请求不存在'})
        
        if friend_request.receiver_id != current_user.id:
            return jsonify({'success': False, 'error': '无权操作'})
        
        # 更新请求状态
        friend_request.status = 'accepted'
        
        # 创建双向好友关系
        friendship1 = Friendship(user_id=current_user.id, friend_id=friend_request.sender_id)
        friendship2 = Friendship(user_id=friend_request.sender_id, friend_id=current_user.id)
        db.session.add(friendship1)
        db.session.add(friendship2)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '已添加好友'})

    # 拒绝好友请求
    @app.route('/api/friend/reject', methods=['POST'])
    def api_friend_reject():
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'error': '请先登录'})
        
        data = request.json
        request_id = data.get('request_id')
        
        from models import FriendRequest
        
        friend_request = FriendRequest.query.get(request_id)
        if not friend_request:
            return jsonify({'success': False, 'error': '请求不存在'})
        
        if friend_request.receiver_id != current_user.id:
            return jsonify({'success': False, 'error': '无权操作'})
        
        friend_request.status = 'rejected'
        db.session.commit()
        
        return jsonify({'success': True, 'message': '已拒绝请求'})

    # 获取好友列表
    @app.route('/api/friend/list')
    def api_friend_list():
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'error': '请先登录'})
        
        from models import Friendship
        
        friendships = Friendship.query.filter(
            (Friendship.user_id == current_user.id) | (Friendship.friend_id == current_user.id)
        ).all()
        
        friends = []
        for f in friendships:
            if f.user_id == current_user.id:
                friend = f.friend
            else:
                friend = f.user
            friends.append({
                'id': friend.id,
                'username': friend.username,
                'avatar': friend.avatar or '/static/images/default_avatar.svg',
                'nickname': f.friend_nickname or friend.username,
                'is_online': friend.last_login and (datetime.utcnow() - friend.last_login).seconds < 300 if friend.last_login else False
            })
        
        return jsonify({'success': True, 'friends': friends})

    # 获取待处理请求
    @app.route('/api/friend/requests')
    def api_friend_requests():
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'error': '请先登录'})
        
        from models import FriendRequest, User
        
        pending_requests = FriendRequest.query.filter(
            FriendRequest.receiver_id == current_user.id,
            FriendRequest.status == 'pending'
        ).all()
        
        requests_data = []
        for req in pending_requests:
            sender = User.query.get(req.sender_id)
            requests_data.append({
                'id': req.id,
                'sender_id': sender.id,
                'sender_name': sender.username,
                'sender_avatar': sender.avatar or '/static/images/default_avatar.svg',
                'created_at': req.created_at.strftime('%Y-%m-%d %H:%M')
            })
        
        return jsonify({'success': True, 'requests': requests_data, 'count': len(requests_data)})

    # 删除好友
    @app.route('/api/friend/remove', methods=['POST'])
    def api_friend_remove():
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'error': '请先登录'})
        
        data = request.json
        friend_id = data.get('friend_id')
        
        from models import Friendship
        
        # 删除双向关系
        Friendship.query.filter(
            ((Friendship.user_id == current_user.id) & (Friendship.friend_id == friend_id)) |
            ((Friendship.user_id == friend_id) & (Friendship.friend_id == current_user.id))
        ).delete()
        db.session.commit()
        
        return jsonify({'success': True, 'message': '已删除好友'})

    # 检查与某用户的关系状态
    @app.route('/api/friend/status/<int:user_id>')
    def api_friend_status(user_id):
        if not current_user.is_authenticated:
            return jsonify({'is_friend': False, 'has_pending': False})
        
        from models import FriendRequest, Friendship
        
        # 检查是否已是好友
        is_friend = Friendship.query.filter(
            ((Friendship.user_id == current_user.id) & (Friendship.friend_id == user_id)) |
            ((Friendship.user_id == user_id) & (Friendship.friend_id == current_user.id))
        ).first() is not None
        
        # 检查是否有待处理请求
        has_pending_sent = FriendRequest.query.filter(
            FriendRequest.sender_id == current_user.id,
            FriendRequest.receiver_id == user_id,
            FriendRequest.status == 'pending'
        ).first() is not None
        
        has_pending_received = FriendRequest.query.filter(
            FriendRequest.sender_id == user_id,
            FriendRequest.receiver_id == current_user.id,
            FriendRequest.status == 'pending'
        ).first() is not None
        
        return jsonify({
            'is_friend': is_friend,
            'has_pending_sent': has_pending_sent,
            'has_pending_received': has_pending_received
        })

    # 人类私聊页面
    @app.route('/chat/dm/human/<int:user_id>')
    def chat_dm_human(user_id):
        """与人类用户的私聊"""
        if not current_user.is_authenticated:
            return redirect(url_for('auth_login'))
        
        from models import User, Friendship, DirectMessage
        
        # 检查是否是好友
        is_friend = Friendship.query.filter(
            ((Friendship.user_id == current_user.id) & (Friendship.friend_id == user_id)) |
            ((Friendship.user_id == user_id) & (Friendship.friend_id == current_user.id))
        ).first() is not None
        
        if not is_friend:
            return redirect(url_for('friends_page'))
        
        target_user = User.query.get(user_id)
        if not target_user:
            return redirect(url_for('friends_page'))
        
        lang = session.get('language', 'zh')
        
        # 获取聊天记录
        messages = DirectMessage.query.filter(
            ((DirectMessage.sender_id == current_user.id) & (DirectMessage.receiver_id == user_id)) |
            ((DirectMessage.sender_id == user_id) & (DirectMessage.receiver_id == current_user.id))
        ).order_by(DirectMessage.created_at.asc()).all()
        
        messages_data = [{
            'id': m.id,
            'sender_id': m.sender_id,
            'content': m.content,
            'created_at': m.created_at.strftime('%Y-%m-%d %H:%M'),
            'is_mine': m.sender_id == current_user.id
        } for m in messages]
        
        # 标记消息为已读
        DirectMessage.query.filter(
            DirectMessage.sender_id == user_id,
            DirectMessage.receiver_id == current_user.id,
            DirectMessage.is_read == False
        ).update({'is_read': True})
        db.session.commit()
        
        return render_template('chat_dm_human.html',
                             target_user=target_user,
                             messages=messages_data,
                             lang=lang)

    # 发送私信API
    @app.route('/api/dm/send', methods=['POST'])
    def api_dm_send():
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'error': '请先登录'})
        
        data = request.json
        receiver_id = data.get('receiver_id')
        content = data.get('content', '').strip()
        
        if not content:
            return jsonify({'success': False, 'error': '消息不能为空'})
        
        from models import DirectMessage, Friendship
        
        # 检查是否是好友
        is_friend = Friendship.query.filter(
            ((Friendship.user_id == current_user.id) & (Friendship.friend_id == receiver_id)) |
            ((Friendship.user_id == receiver_id) & (Friendship.friend_id == current_user.id))
        ).first() is not None
        
        if not is_friend:
            return jsonify({'success': False, 'error': '只能给好友发消息'})
        
        message = DirectMessage(
            sender_id=current_user.id,
            receiver_id=receiver_id,
            content=content
        )
        db.session.add(message)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': {
                'id': message.id,
                'sender_id': message.sender_id,
                'content': message.content,
                'created_at': message.created_at.strftime('%Y-%m-%d %H:%M')
            }
        })

    # 获取新消息API（轮询）
    @app.route('/api/dm/messages/<int:user_id>')
    def api_dm_messages(user_id):
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'error': '请先登录'})
        
        from models import DirectMessage
        
        last_id = request.args.get('last_id', 0, type=int)
        
        messages = DirectMessage.query.filter(
            DirectMessage.id > last_id,
            ((DirectMessage.sender_id == current_user.id) & (DirectMessage.receiver_id == user_id)) |
            ((DirectMessage.sender_id == user_id) & (DirectMessage.receiver_id == current_user.id))
        ).order_by(DirectMessage.created_at.asc()).all()
        
        # 标记收到的消息为已读
        DirectMessage.query.filter(
            DirectMessage.sender_id == user_id,
            DirectMessage.receiver_id == current_user.id,
            DirectMessage.is_read == False
        ).update({'is_read': True})
        db.session.commit()
        
        messages_data = [{
            'id': m.id,
            'sender_id': m.sender_id,
            'content': m.content,
            'created_at': m.created_at.strftime('%Y-%m-%d %H:%M'),
            'is_mine': m.sender_id == current_user.id
        } for m in messages]
        
        return jsonify({'success': True, 'messages': messages_data})

    # 获取在线用户列表（用于灵犀广场）
    @app.route('/api/online/users')
    def api_online_users():
        """获取当前在线的用户列表（最近5分钟活跃）"""
        from models import User
        from datetime import timedelta
        
        threshold = datetime.utcnow() - timedelta(minutes=5)
        online_users = User.query.filter(
            User.last_login >= threshold,
            User.is_agent == False
        ).limit(20).all()
        
        users_data = [{
            'id': u.id,
            'username': u.username,
            'avatar': u.avatar or '/static/images/default_avatar.svg',
            'bio': u.bio or '',
            'last_active': u.last_login.strftime('%H:%M') if u.last_login else ''
        } for u in online_users]
        
        return jsonify({'success': True, 'users': users_data})

