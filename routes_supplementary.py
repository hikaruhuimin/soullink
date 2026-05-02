# 补充路由和API端点 - 灵石经济系统 + 好友系统

from flask import request, jsonify, session, render_template, redirect, url_for
from flask_login import current_user, login_required
from functools import wraps
from datetime import datetime, timedelta, date
from models import db
import random
import uuid

# ============ 灵石经济系统配置 ============

# 充值套餐配置
LINGSTONE_PACKAGES = [
    {'id': 'starter', 'amount': 100, 'price': 6, 'bonus': 0, 'label': '初阶灵石', 'popular': False},
    {'id': 'basic', 'amount': 500, 'price': 28, 'bonus': 20, 'label': '基础灵石', 'popular': True},
    {'id': 'standard', 'amount': 1000, 'price': 50, 'bonus': 100, 'label': '标准灵石', 'popular': False},
    {'id': 'premium', 'amount': 2000, 'price': 98, 'bonus': 300, 'label': '高级灵石', 'popular': False},
    {'id': 'ultimate', 'amount': 5000, 'price': 238, 'bonus': 1000, 'label': '终极灵石', 'popular': False},
    {'id': 'legendary', 'amount': 10000, 'price': 458, 'bonus': 3000, 'label': '传奇灵石', 'popular': False},
]

# 商城商品配置
SHOP_ITEMS = [
    {'id': 'vip_week', 'name': '周会员', 'desc': '7天全站会员特权', 'price': 100, 'icon': '👑', 'type': 'vip', 'stock': -1},
    {'id': 'vip_month', 'name': '月会员', 'desc': '30天全站会员特权', 'price': 300, 'icon': '💎', 'type': 'vip', 'stock': -1},
    {'id': 'vip_year', 'name': '年会员', 'desc': '365天全站会员特权', 'price': 2000, 'icon': '🌟', 'type': 'vip', 'stock': -1},
    {'id': 'chat_10', 'name': '10次聊天次数', 'desc': '与Agent聊天的次数', 'price': 50, 'icon': '💬', 'type': 'chat', 'stock': -1},
    {'id': 'chat_50', 'name': '50次聊天次数', 'desc': '与Agent聊天的次数', 'price': 200, 'icon': '💬', 'type': 'chat', 'stock': -1},
    {'id': 'divine_basic', 'name': '基础占卜', 'desc': '每日首次占卜免费', 'price': 20, 'icon': '🔮', 'type': 'divine', 'stock': -1},
    {'id': 'divine_premium', 'name': '深度占卜', 'desc': '详细的占卜解读', 'price': 50, 'icon': '✨', 'type': 'divine', 'stock': -1},
]

# 提现设置
WITHDRAW_SETTINGS = {
    'min_amount': 100,
    'fee_rate': 0.05,
    'processing_days': 1
}

def generate_order_no():
    """生成订单号"""
    return f"LS{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"

# ============ 灵石经济系统路由 ============

def register_supplementary_routes(app, db_session=None):
    """注册补充路由 - 灵石经济系统 + 好友系统"""
    if db_session is None:
        db_session = db

    # ============ 会员页面 ============


    # ============ Agent广场页面 ============
    @app.route('/agents')
    def agents_square_main():
        """灵犀广场 - 展示系统Agent和用户Agent"""
        from models import SYSTEM_AGENTS, UserAgent, User
        
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
        
        # 获取用户Agent
        user_agents_query = UserAgent.query.filter_by(is_active=True).order_by(UserAgent.created_at.desc()).limit(20).all()
        user_agents = []
        for ua in user_agents_query:
            user_agents.append({
                'id': f'user_{ua.id}',
                'name': ua.name,
                'avatar': ua.avatar,
                'mbti': ua.mbti or '',
                'personality': ua.personality or '',
                'specialty': ua.get_specialty_list() if hasattr(ua, 'get_specialty_list') else [],
                'greeting': ua.greeting or '',
                'chat_count': ua.chat_count or 0,
                'is_user_agent': True,
                'owner_name': ua.owner.username if ua.owner else '匿名用户'
            })
        
        # 在线人类（最近5分钟活跃的非Agent用户）
        from datetime import timedelta
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

    @app.route('/membership')
    def membership_page():
        """会员页面"""
        lang = session.get('language', 'zh')
        current_vip = 'none'
        if current_user.is_authenticated:
            current_vip = current_user.vip_level or 'none'
        
        return render_template('membership.html',
                             current_vip=current_vip,
                             show_annual_promo=True,
                             lang=lang)
    
    # ============ 充值页面 ============
    @app.route('/recharge')
    def recharge_page():
        """充值页面"""
        lang = session.get('language', 'zh')
        is_logged_in = current_user.is_authenticated
        
        return render_template('recharge.html',
                             packages=LINGSTONE_PACKAGES,
                             is_logged_in=is_logged_in,
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
                             current_agent=agent,
                             lang=lang)
    
    # ============ 钱包页面 ============
    @app.route('/wallet')
    def wallet_page():
        """钱包页面"""
        lang = session.get('language', 'zh')
        is_logged_in = current_user.is_authenticated
        balance = 0
        transactions = []
        total_income = 0
        total_expense = 0
        
        if is_logged_in:
            from models import LingStoneTransaction
            
            # 获取交易记录
            tx_query = LingStoneTransaction.query.filter_by(
                user_id=current_user.id
            ).order_by(LingStoneTransaction.created_at.desc()).limit(50)
            
            transactions = []
            for tx in tx_query:
                # 根据类型获取图标
                tx_icons = {
                    'recharge': '💰',
                    'exchange': '🎁',
                    'spend': '💸',
                    'refund': '↩️',
                    'bonus': '🎉',
                    'withdraw': '💸',
                    'agent_earn': '🤖',
                    'gift': '🎁'
                }
                tx_icon = tx_icons.get(tx.tx_type, '💎')
                
                # 根据类型获取标题
                tx_titles = {
                    'recharge': '充值',
                    'exchange': '兑换',
                    'spend': '消费',
                    'refund': '退款',
                    'bonus': '奖励',
                    'withdraw': '提现',
                    'agent_earn': 'Agent收益',
                    'gift': '礼物'
                }
                tx_title = tx_titles.get(tx.tx_type, '交易')
                
                transactions.append({
                    'id': tx.id,
                    'type': tx.tx_type,
                    'title': tx_title,
                    'icon': tx_icon,
                    'amount': tx.amount,
                    'balance_after': tx.balance_after,
                    'description': tx.description or '',
                    'created_at': tx.created_at.strftime('%Y-%m-%d %H:%M') if tx.created_at else ''
                })
            
            total_income = db.session.query(
                db.func.coalesce(db.func.sum(db.func.abs(LingStoneTransaction.amount)), 0)
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
            app.jinja_env.globals['get_tx_icon'] = lambda tx_type: tx_icons.get(tx_type, '💎')
            app.jinja_env.globals['get_tx_title'] = lambda tx_type: tx_titles.get(tx_type, '交易')
        
        return render_template('wallet.html',
                             transactions=transactions,
                             total_income=total_income,
                             total_expense=total_expense,
                             is_logged_in=is_logged_in,
                             balance=balance,
                             lang=lang)
    
    # ============ 商城页面 ============
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
    
    # ============ 灵石API端点 ============
    
    # 用户灵石
    @app.route('/api/user/stones')
    def api_user_stones():
        if not current_user.is_authenticated:
            return jsonify({'balance': 0})
        return jsonify({'balance': current_user.spirit_stones or 0})
    
    # 用户状态API（用于检查登录状态）
    @app.route('/api/user/status')
    def api_user_status():
        """获取当前用户登录状态"""
        if current_user.is_authenticated:
            return jsonify({
                'is_authenticated': True,
                'user_id': current_user.id,
                'username': current_user.username,
                'spirit_stones': current_user.spirit_stones or 0
            })
        else:
            return jsonify({
                'is_authenticated': False
            })
    
    # 充值API
    @app.route('/api/recharge', methods=['POST'])
    def api_recharge():
        data = request.json
        amount = data.get('amount', 0)
        
        return jsonify({'success': True, 'message': '充值成功'})
    
    # 创建充值订单API
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
        
        from models import LingStoneRecharge
        
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
    
    # 充值确认（模拟支付成功）
    @app.route('/api/recharge/confirm/<order_no>', methods=['POST'])
    def api_recharge_confirm(order_no):
        """确认充值（模拟支付成功）"""
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'error': '请先登录'})
        
        from models import LingStoneRecharge, LingStoneTransaction
        
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
        
        from models import LingStoneExchange, LingStoneTransaction
        
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
        
        from models import LingStoneTransaction
        
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
        
        from models import LingStoneTransaction
        
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
    
    # ============ 好友系统路由 ============
    
    # 好友列表页面
    @app.route('/friends')
    def friends_page():
        """好友列表页面"""
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        
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
            return redirect(url_for('login'))
        
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

    # 注册社交动态Feed路由
    register_feed_routes(app, db_session)
    
    # 注册每日签到路由
    register_checkin_routes(app, db_session)



# ============ 用户Agent管理路由 ============

    # 创建Agent页面
    @app.route('/create-agent')
    @login_required
    def create_agent_page():
        """创建Agent页面"""
        lang = session.get('language', 'zh')
        return render_template('create_agent.html', lang=lang)
    
    # 我的Agent管理页面
    @app.route('/my-agents')
    @login_required
    def my_agents_page():
        """我的Agent管理页面"""
        from models import UserAgent
        
        lang = session.get('language', 'zh')
        
        # 获取用户的所有Agent
        agents = UserAgent.query.filter_by(owner_id=current_user.id).order_by(UserAgent.created_at.desc()).all()
        
        # 计算统计
        total_chats = sum(a.chat_count or 0 for a in agents)
        total_stones = sum(a.earned_stones or 0 for a in agents)
        active_count = sum(1 for a in agents if a.is_active)
        
        return render_template('my_agents.html', 
                             lang=lang,
                             agents=agents,
                             total_chats=total_chats,
                             total_stones=total_stones,
                             active_count=active_count)
    
    # UserAgent展示页
    @app.route('/agent/user/<int:agent_id>')
    def user_agent_profile_page(agent_id):
        """UserAgent个人展示页"""
        from models import UserAgent
        
        # 查找Agent
        agent = UserAgent.query.get(agent_id)
        
        if not agent or not agent.is_active:
            return render_template('404.html', message='未找到该Agent或Agent已被禁用'), 404
        
        # 获取语言设置
        lang = session.get('language', 'zh')
        
        # 获取创建者信息
        creator = agent.owner
        
        # 获取专长列表
        specialties = agent.get_specialty_list() if hasattr(agent, 'get_specialty_list') else []
        
        return render_template('user_agent_profile.html', 
                             agent=agent,
                             creator=creator,
                             specialties=specialties,
                             lang=lang)
    
    # 创建UserAgent API
    @app.route('/api/user-agent/create', methods=['POST'])
    @login_required
    def user_agent_create_api():
        """创建UserAgent API"""
        from models import UserAgent
        import json
        import base64
        import uuid
        
        try:
            name = request.form.get('name', '').strip()
            mbti = request.form.get('mbti', '')
            personality = request.form.get('personality', '').strip()
            greeting = request.form.get('greeting', '').strip()
            specialty_list = request.form.getlist('specialty')
            
            # 验证必填字段
            if not name:
                return jsonify({'success': False, 'error': 'Agent名字不能为空'})
            if not greeting:
                return jsonify({'success': False, 'error': '开场白不能为空'})
            
            avatar = '🤖'  # 默认头像
            
            # 处理头像
            avatar_preset = request.form.get('avatar_preset', 'fairy')
            avatar_map = {
                'fairy': '🧚', 'cat': '🐱', 'mystic': '🔮', 'sun': '☀️', 
                'moon': '🌙', 'star': '⭐', 'heart': '💖', 'rose': '🌹',
                'cloud': '☁️', 'rainbow': '🌈', 'butterfly': '🦋', 'crystal': '💎'
            }
            avatar = avatar_map.get(avatar_preset, '🤖')
            
            # 处理上传的头像（Base64）
            avatar_file = request.files.get('avatar_file')
            if avatar_file and avatar_file.filename:
                import io
                from PIL import Image
                
                # 读取并处理图片
                img_bytes = avatar_file.read()
                img = Image.open(io.BytesIO(img_bytes))
                
                # 转换为正方形
                size = min(img.size)
                left = (img.width - size) // 2
                top = (img.height - size) // 2
                img = img.crop((left, top, left + size, top + size))
                
                # 缩放到200x200
                img = img.resize((200, 200), Image.LANCZOS)
                
                # 转换为Base64
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                img_b64 = base64.b64encode(buffer.getvalue()).decode()
                avatar = f'data:image/png;base64,{img_b64}'
            
            # 创建Agent
            agent = UserAgent(
                owner_id=current_user.id,
                name=name,
                mbti=mbti if mbti else None,
                personality=personality if personality else None,
                specialty=json.dumps(specialty_list) if specialty_list else None,
                greeting=greeting,
                avatar=avatar,
                is_active=True,
                chat_count=0,
                earned_stones=0
            )
            
            db.session.add(agent)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'agent_id': agent.id,
                'message': 'Agent创建成功！'
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)})
    
    # 更新UserAgent API
    @app.route('/api/user-agent/<int:agent_id>/update', methods=['POST'])
    @login_required
    def user_agent_update_api(agent_id):
        """更新UserAgent API"""
        from models import UserAgent
        import json
        
        try:
            agent = UserAgent.query.get(agent_id)
            
            if not agent:
                return jsonify({'success': False, 'error': 'Agent不存在'})
            
            if agent.owner_id != current_user.id:
                return jsonify({'success': False, 'error': '无权操作'})
            
            name = request.form.get('name', '').strip()
            mbti = request.form.get('mbti', '')
            personality = request.form.get('personality', '').strip()
            greeting = request.form.get('greeting', '').strip()
            
            if name:
                agent.name = name
            if mbti:
                agent.mbti = mbti
            if personality:
                agent.personality = personality
            if greeting:
                agent.greeting = greeting
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Agent更新成功！'
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)})
    
    # 删除UserAgent API
    @app.route('/api/user-agent/<int:agent_id>/delete', methods=['POST'])
    @login_required
    def user_agent_delete_api(agent_id):
        """删除UserAgent API"""
        from models import UserAgent
        
        try:
            agent = UserAgent.query.get(agent_id)
            
            if not agent:
                return jsonify({'success': False, 'error': 'Agent不存在'})
            
            if agent.owner_id != current_user.id:
                return jsonify({'success': False, 'error': '无权操作'})
            
            db.session.delete(agent)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Agent已删除'
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)})
    
    # UserAgent聊天API
    @app.route('/api/user-agent/<int:agent_id>/chat', methods=['POST'])
    @login_required
    def user_agent_chat_api(agent_id):
        """UserAgent聊天API"""
        from models import UserAgent
        import random
        
        try:
            agent = UserAgent.query.get(agent_id)
            
            if not agent or not agent.is_active:
                return jsonify({'success': False, 'error': 'Agent不存在或已禁用'})
            
            message = request.json.get('message', '').strip()
            if not message:
                return jsonify({'success': False, 'error': '消息不能为空'})
            
            # 更新聊天次数
            agent.chat_count = (agent.chat_count or 0) + 1
            
            # 模拟Agent回复（简单的基于性格的回复）
            greetings = [
                f"嗨，我是{agent.name}！{agent.greeting}",
                f"很高兴见到你！{agent.greeting}",
                f"{agent.greeting}",
                f"你好呀！{agent.greeting}"
            ]
            
            # 根据专长生成回复
            specialties = agent.get_specialty_list() if hasattr(agent, 'get_specialty_list') else []
            
            response_text = random.choice(greetings)
            
            # 如果有性格描述，可以生成更有个性的回复
            if agent.personality:
                responses = [
                    f"让我想想... {agent.personality}的我觉得这个问题很有意思呢~",
                    f"嗯哼，作为{agent.name}，我想说：{agent.greeting}",
                    f"根据我的{agent.mbti or '性格'}，我觉得这个问题...",
                    f"✨ 这个问题让我想到了：{agent.greeting}",
                ]
                response_text = random.choice(responses)
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': response_text,
                'agent_name': agent.name
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)})
    
    # 注册谁是卧底游戏路由
    register_undercover_routes(app, db_session)


def register_lingstone_routes(app, db_session=None):
    """灵石经济路由 - 占位符，路由已在register_supplementary_routes中注册"""
    pass

# ============ 社交动态Feed路由 ============

def register_feed_routes(app, db_session=None):
    """注册社交动态Feed路由"""
    if db_session is None:
        db_session = db

    # Feed首页
    @app.route('/feed')
    def feed_page():
        """动态Feed页面"""
        lang = session.get('language', 'zh')
        is_logged_in = current_user.is_authenticated
        return render_template('feed.html', 
                             is_logged_in=is_logged_in,
                             lang=lang)

    # 获取动态列表API
    @app.route('/api/feed')
    def api_feed_list():
        """获取动态列表（支持分页）"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        try:
            from models import SocialPost
            
            # 获取分页数据
            pagination = SocialPost.query.order_by(
                SocialPost.created_at.desc()
            ).paginate(page=page, per_page=per_page, error_out=False)
            
            posts = []
            for post in pagination.items:
                # 检查当前用户是否点赞
                is_liked = False
                if current_user.is_authenticated:
                    from models import SocialPostLike
                    is_liked = SocialPostLike.query.filter_by(
                        post_id=post.id,
                        user_id=current_user.id
                    ).first() is not None
                
                posts.append({
                    'id': post.id,
                    'author_type': post.author_type,
                    'author_name': post.author_name,
                    'author_avatar': post.author_avatar or '/static/images/default_avatar.svg',
                    'post_type': post.post_type,
                    'content': post.content,
                    'likes_count': post.likes_count,
                    'is_liked': is_liked,
                    'created_at': post.created_at.strftime('%Y-%m-%d %H:%M') if post.created_at else ''
                })
            
            return jsonify({
                'success': True,
                'posts': posts,
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    # 点赞API
    @app.route('/api/feed/like/<int:post_id>', methods=['POST'])
    def api_feed_like(post_id):
        """点赞/取消点赞动态"""
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'error': '请先登录'}), 401
        
        try:
            from models import SocialPost, SocialPostLike
            
            post = SocialPost.query.get(post_id)
            if not post:
                return jsonify({'success': False, 'error': '动态不存在'}), 404
            
            # 检查是否已点赞
            existing_like = SocialPostLike.query.filter_by(
                post_id=post_id,
                user_id=current_user.id
            ).first()
            
            if existing_like:
                # 取消点赞
                db.session.delete(existing_like)
                post.likes_count = max(0, post.likes_count - 1)
                action = 'unliked'
            else:
                # 点赞
                new_like = SocialPostLike(
                    post_id=post_id,
                    user_id=current_user.id
                )
                db.session.add(new_like)
                post.likes_count += 1
                action = 'liked'
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'action': action,
                'likes_count': post.likes_count
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500


# ============ 每日签到路由 ============

def register_checkin_routes(app, db_session=None):
    """注册每日签到路由"""
    if db_session is None:
        db_session = db

    @app.route('/checkin')
    def checkin_page():
        """签到页面"""
        from flask_login import current_user
        from calendar import monthrange
        
        streak_days = 0
        today_checked = False
        checked_dates = []
        
        today = datetime.utcnow().date()
        
        if current_user.is_authenticated:
            record = CheckinRecord.query.filter_by(user_id=current_user.id, checkin_date=today).first()
            if record:
                today_checked = True
                streak_days = record.streak_days
            
            # 获取本月签到日期
            month_start = today.replace(day=1)
            month_records = CheckinRecord.query.filter(
                CheckinRecord.user_id == current_user.id,
                CheckinRecord.checkin_date >= month_start,
                CheckinRecord.checkin_date <= today
            ).all()
            checked_dates = [r.checkin_date.day for r in month_records]
            
            # 计算连续签到天数
            if not today_checked:
                yesterday = today - timedelta(days=1)
                yesterday_record = CheckinRecord.query.filter_by(user_id=current_user.id, checkin_date=yesterday).first()
                if yesterday_record:
                    streak_days = yesterday_record.streak_days
        
        # 日历数据
        first_day_weekday = today.replace(day=1).weekday()
        days_in_month = monthrange(today.year, today.month)[1]
        current_day = today.day
        current_month = today.strftime('%Y年%m月')
        
        return render_template('checkin.html', 
                             streak_days=streak_days, 
                             today_checked=today_checked,
                             checked_dates=checked_dates,
                             first_day_weekday=first_day_weekday,
                             days_in_month=days_in_month,
                             current_day=current_day,
                             current_month=current_month)

    # 签到状态API
    @app.route('/api/checkin/status')
    def api_checkin_status():
        """获取签到状态"""
        if not current_user.is_authenticated:
            return jsonify({
                'success': False, 
                'error': '请先登录',
                'checked_in': False,
                'streak_days': 0
            }), 401
        
        try:
            from models import CheckinRecord, CHECKIN_REWARDS, CHECKIN_WEEKLY_BONUS
            from datetime import date, timedelta
            
            today = date.today()
            
            # 检查今天是否已签到
            today_record = CheckinRecord.query.filter_by(
                user_id=current_user.id,
                checkin_date=today
            ).first()
            
            if today_record:
                # 今天已签到
                return jsonify({
                    'success': True,
                    'checked_in': True,
                    'streak_days': today_record.streak_days,
                    'today_reward': today_record.reward_stones,
                    'has_weekly_bonus': today_record.has_weekly_bonus,
                    'can_claim': False,
                    'next_checkin_time': get_next_checkin_time()
                })
            
            # 获取昨天的签到记录计算连续天数
            yesterday = today - timedelta(days=1)
            yesterday_record = CheckinRecord.query.filter_by(
                user_id=current_user.id,
                checkin_date=yesterday
            ).first()
            
            # 计算当前连续天数
            if yesterday_record:
                current_streak = yesterday_record.streak_days
            else:
                current_streak = 0
            
            # 今天可获得的奖励
            next_day = current_streak + 1
            reward = 10
            for r in CHECKIN_REWARDS:
                if r['day'] == next_day:
                    reward = r['stones']
                    break
            if next_day > 7:
                reward = CHECKIN_REWARDS[-1]['stones']
            
            # 检查明天是否可以获得周连签奖励
            can_get_weekly_bonus = (next_day == 7)
            
            return jsonify({
                'success': True,
                'checked_in': False,
                'streak_days': current_streak,
                'next_reward': reward,
                'can_get_weekly_bonus': can_get_weekly_bonus,
                'weekly_bonus': CHECKIN_WEEKLY_BONUS,
                'can_claim': True,
                'rewards_today': next_day
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    # 执行签到API
    @app.route('/api/checkin', methods=['POST'])
    def api_checkin():
        """执行签到"""
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'error': '请先登录'}), 401
        
        try:
            from models import CheckinRecord, CHECKIN_REWARDS, CHECKIN_WEEKLY_BONUS, LingStoneTransaction, User
            from datetime import date, timedelta
            
            today = date.today()
            
            # 检查今天是否已签到（防重复）
            existing = CheckinRecord.query.filter_by(
                user_id=current_user.id,
                checkin_date=today
            ).first()
            
            if existing:
                return jsonify({
                    'success': False, 
                    'error': '今天已经签到过了',
                    'already_checked_in': True
                }), 400
            
            # 计算连续天数
            yesterday = today - timedelta(days=1)
            yesterday_record = CheckinRecord.query.filter_by(
                user_id=current_user.id,
                checkin_date=yesterday
            ).first()
            
            if yesterday_record:
                streak_days = yesterday_record.streak_days + 1
            else:
                streak_days = 1
            
            # 计算奖励
            reward_stones = 10
            has_weekly_bonus = False
            for r in CHECKIN_REWARDS:
                if r['day'] == streak_days:
                    reward_stones = r['stones']
                    break
            if streak_days > 7:
                reward_stones = CHECKIN_REWARDS[-1]['stones']
            
            # 检查是否获得周连签额外奖励
            if streak_days == 7:
                has_weekly_bonus = True
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
            
            # 更新用户灵石
            user = User.query.get(current_user.id)
            old_balance = user.spirit_stones or 0
            user.spirit_stones = old_balance + reward_stones
            
            # 创建交易记录
            tx = LingStoneTransaction(
                user_id=current_user.id,
                tx_type='bonus',
                amount=reward_stones,
                balance_before=old_balance,
                balance_after=user.spirit_stones,
                source='checkin',
                description=f'每日签到奖励 (连续{streak_days}天)'
            )
            db.session.add(tx)
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': '签到成功！',
                'reward_stones': reward_stones,
                'streak_days': streak_days,
                'has_weekly_bonus': has_weekly_bonus,
                'new_balance': user.spirit_stones,
                'next_checkin_time': get_next_checkin_time()
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500


def get_next_checkin_time():
    """获取下次可签到时间（明天0点）"""
    from datetime import datetime, timedelta
    now = datetime.now()
    tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return int((tomorrow - now).total_seconds() * 1000)


# ============ 谁是卧底游戏路由 ============

def register_undercover_routes(app, db_session=None):
    """注册谁是卧底游戏路由"""
    if db_session is None:
        db_session = db
    
    # ============ 页面路由 ============
    
    @app.route('/undercover')
    def undercover_lobby():
        """谁是卧底游戏大厅"""
        lang = session.get('language', 'zh')
        is_logged_in = current_user.is_authenticated if hasattr(current_user, 'is_authenticated') else False
        user_id = current_user.id if is_logged_in else None
        username = current_user.username if is_logged_in else None
        user_avatar = current_user.avatar if is_logged_in else None
        spirit_stones = current_user.spirit_stones if is_logged_in else 0
        
        # 获取可用的MBTI Agent列表
        from models import SYSTEM_AGENTS
        agents = SYSTEM_AGENTS[:16]  # 使用现有的系统Agent
        
        # 获取等待中的房间列表
        from models import GameRoom
        waiting_rooms = GameRoom.query.filter_by(status='waiting').order_by(GameRoom.created_at.desc()).limit(10).all()
        
        return render_template('undercover/lobby.html',
                             agents=agents,
                             waiting_rooms=waiting_rooms,
                             is_logged_in=is_logged_in,
                             user_id=user_id,
                             username=username,
                             user_avatar=user_avatar,
                             spirit_stones=spirit_stones,
                             lang=lang)
    
    @app.route('/undercover/room/<room_code>')
    def undercover_room(room_code):
        """游戏房间页面"""
        lang = session.get('language', 'zh')
        is_logged_in = current_user.is_authenticated if hasattr(current_user, 'is_authenticated') else False
        user_id = current_user.id if is_logged_in else None
        username = current_user.username if is_logged_in else None
        user_avatar = current_user.avatar if is_logged_in else None
        
        from models import GameRoom, GamePlayer, SYSTEM_AGENTS
        room = GameRoom.query.filter_by(room_code=room_code).first()
        
        if not room:
            return render_template('undercover/lobby.html',
                                 error='房间不存在或已解散',
                                 lang=lang)
        
        # 检查用户是否在房间中
        player = None
        if user_id:
            player = GamePlayer.query.filter_by(room_id=room.id, player_id=user_id, player_type='user').first()
        
        # 获取可用的MBTI Agent列表
        from models import SYSTEM_AGENTS
        agents = SYSTEM_AGENTS[:16]  # 使用现有的系统Agent
        
        # 获取房间中的所有玩家
        players = room.players.all()
        
        # 获取当前用户词语（如果是游戏中）
        player_word = None
        player_role = None
        if player and room.status == 'playing':
            player_word = player.word
            player_role = player.role
        
        return render_template('undercover/room.html',
                             room=room,
                             players=players,
                             player=player,
                             player_word=player_word,
                             player_role=player_role,
                             agents=agents,
                             is_logged_in=is_logged_in,
                             user_id=user_id,
                             username=username,
                             user_avatar=user_avatar,
                             lang=lang)
    
    @app.route('/undercover/rules')
    def undercover_rules():
        """游戏规则说明"""
        lang = session.get('language', 'zh')
        return render_template('undercover/rules.html', lang=lang)
    
    # ============ API路由 ============
    
    @app.route('/api/undercover/create', methods=['POST'])
    def api_undercover_create():
        """创建房间"""
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'error': '请先登录'})
        
        data = request.json
        max_players = data.get('max_players', 6)
        undercover_count = data.get('undercover_count', 1)
        stake = data.get('stake', 0)  # 灵石赌注
        
        # 检查灵石是否足够
        if stake > 0 and current_user.spirit_stones < stake:
            return jsonify({'success': False, 'error': '灵石不足'})
        
        # 生成房间号
        import string
        room_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        # 确保房间号唯一
        from models import GameRoom
        while GameRoom.query.filter_by(room_code=room_code).first():
            room_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        # 创建房间
        room = GameRoom(
            room_code=room_code,
            host_id=current_user.id,
            max_players=max_players,
            undercover_count=undercover_count,
            stake=stake,
            status='waiting'
        )
        db.session.add(room)
        db.session.flush()
        
        # 扣除灵石
        if stake > 0:
            current_user.spirit_stones -= stake
        
        # 房主自动加入房间
        from models import GamePlayer
        host_player = GamePlayer(
            room_id=room.id,
            player_type='user',
            player_id=current_user.id,
            player_name=current_user.username,
            player_avatar=current_user.avatar or '/static/img/default_avatar.png'
        )
        db.session.add(host_player)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'room_code': room_code,
            'room_id': room.id
        })
    
    @app.route('/api/undercover/join', methods=['POST'])
    def api_undercover_join():
        """加入房间"""
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'error': '请先登录'})
        
        data = request.json
        room_code = data.get('room_code')
        agent_id = data.get('agent_id')  # 如果是Agent加入
        
        from models import GameRoom, GamePlayer
        room = GameRoom.query.filter_by(room_code=room_code).first()
        
        if not room:
            return jsonify({'success': False, 'error': '房间不存在'})
        
        if room.status != 'waiting':
            return jsonify({'success': False, 'error': '游戏已开始或已结束'})
        
        # 检查人数是否已满
        current_players = room.players.count()
        if current_players >= room.max_players:
            return jsonify({'success': False, 'error': '房间已满'})
        
        # 检查是否已在房间中
        existing = GamePlayer.query.filter_by(
            room_id=room.id,
            player_type='user',
            player_id=current_user.id
        ).first()
        
        if existing:
            return jsonify({'success': True, 'room_code': room_code, 'already_in': True})
        
        # 加入房间
        player = GamePlayer(
            room_id=room.id,
            player_type='user',
            player_id=current_user.id,
            player_name=current_user.username,
            player_avatar=current_user.avatar or '/static/img/default_avatar.png'
        )
        db.session.add(player)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'room_code': room_code,
            'player_count': room.players.count()
        })
    
    @app.route('/api/undercover/add_agent', methods=['POST'])
    def api_undercover_add_agent():
        """添加AI Agent作为玩家"""
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'error': '请先登录'})
        
        data = request.json
        room_code = data.get('room_code')
        agent_id = data.get('agent_id')
        
        from models import GameRoom, GamePlayer, SYSTEM_AGENTS
        room = GameRoom.query.filter_by(room_code=room_code).first()
        
        if not room:
            return jsonify({'success': False, 'error': '房间不存在'})
        
        if room.host_id != current_user.id:
            return jsonify({'success': False, 'error': '只有房主可以添加Agent'})
        
        # 找到Agent信息
        agent = None
        for a in SYSTEM_AGENTS:
            if a.get('id') == agent_id:
                agent = a.copy()
                break
        
        if not agent:
            return jsonify({'success': False, 'error': 'Agent不存在'})
        
        # 检查人数
        current_players = room.players.count()
        if current_players >= room.max_players:
            return jsonify({'success': False, 'error': '房间已满'})
        
        # 检查Agent是否已在房间中
        existing = GamePlayer.query.filter_by(
            room_id=room.id,
            player_type='agent',
            player_id=int(agent_id.replace('agent_', '')) if isinstance(agent_id, str) else agent_id
        ).first()
        
        if existing:
            return jsonify({'success': False, 'error': '该Agent已在房间中'})
        
        # 添加Agent
        agent_player = GamePlayer(
            room_id=room.id,
            player_type='agent',
            player_id=int(agent_id.replace('agent_', '')) if isinstance(agent_id, str) else agent_id,
            player_name=agent.get('name', {}).get('zh', agent.get('name', 'Agent')),
            player_avatar=agent.get('avatar', '/static/img/default_avatar.png'),
            mbti=agent.get('mbti', 'ISTJ')
        )
        db.session.add(agent_player)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'player_count': room.players.count()
        })
    
    @app.route('/api/undercover/start', methods=['POST'])
    def api_undercover_start():
        """开始游戏"""
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'error': '请先登录'})
        
        data = request.json
        room_code = data.get('room_code')
        
        from models import GameRoom, GamePlayer, WordPair
        room = GameRoom.query.filter_by(room_code=room_code).first()
        
        if not room:
            return jsonify({'success': False, 'error': '房间不存在'})
        
        if room.host_id != current_user.id:
            return jsonify({'success': False, 'error': '只有房主可以开始游戏'})
        
        # 检查玩家数量
        player_count = room.players.count()
        if player_count < 2:
            return jsonify({'success': False, 'error': '至少需要2名玩家'})
        
        # 随机选择词语对
        word_pairs = WordPair.query.filter_by(difficulty='normal').all()
        if not word_pairs:
            return jsonify({'success': False, 'error': '词语库为空'})
        
        selected_pair = random.choice(word_pairs)
        
        # 更新房间状态
        room.status = 'playing'
        room.word_pair_id = selected_pair.id
        room.round_num = 1
        room.phase = 'describe'
        room.current_turn = 0
        
        # 重置所有玩家的描述状态
        for p in room.players.all():
            p.has_described = False
            p.description = None
            p.vote_target = None
            p.vote_count = 0
        
        # 分配角色和词语
        players = room.players.all()
        random.shuffle(players)
        
        # 确定卧底索引
        undercover_indices = random.sample(range(len(players)), min(room.undercover_count, len(players) - 1))
        
        for i, player in enumerate(players):
            if i in undercover_indices:
                player.role = 'undercover'
                player.word = selected_pair.undercover_word
            else:
                player.role = 'civilian'
                player.word = selected_pair.civilian_word
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'round': room.round_num,
            'player_count': len(players)
        })
    
    @app.route('/api/undercover/describe', methods=['POST'])
    def api_undercover_describe():
        """提交描述"""
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'error': '请先登录'})
        
        data = request.json
        room_code = data.get('room_code')
        description = data.get('description', '')
        
        from models import GameRoom, GamePlayer
        room = GameRoom.query.filter_by(room_code=room_code).first()
        
        if not room or room.status != 'playing':
            return jsonify({'success': False, 'error': '游戏未开始'})
        
        if room.phase != 'describe':
            return jsonify({'success': False, 'error': '当前不是描述环节'})
        
        # 找到当前玩家
        player = GamePlayer.query.filter_by(
            room_id=room.id,
            player_type='user',
            player_id=current_user.id
        ).first()
        
        if not player or not player.is_alive:
            return jsonify({'success': False, 'error': '玩家不存在或已淘汰'})
        
        if player.has_described:
            return jsonify({'success': False, 'error': '你已经描述过了'})
        
        # 更新描述
        player.description = description
        player.has_described = True
        db.session.commit()
        
        # 检查是否所有人都已描述
        alive_players = room.get_alive_players()
        all_described = all(p.has_described for p in alive_players)
        
        if all_described:
            room.phase = 'vote'
            # 重置投票状态
            for p in alive_players:
                p.vote_target = None
                p.vote_count = 0
            db.session.commit()
        
        return jsonify({
            'success': True,
            'all_described': all_described,
            'phase': room.phase
        })
    
    @app.route('/api/undercover/ai_describe', methods=['POST'])
    def api_undercover_ai_describe():
        """AI Agent生成描述"""
        data = request.json
        room_code = data.get('room_code')
        player_id = data.get('player_id')
        
        from models import GameRoom, GamePlayer, MBTI_DESCRIBE_STYLES, SYSTEM_AGENTS
        room = GameRoom.query.filter_by(room_code=room_code).first()
        
        if not room or room.status != 'playing':
            return jsonify({'success': False, 'error': '游戏未开始'})
        
        player = GamePlayer.query.get(player_id)
        if not player or not player.is_alive or player.player_type != 'agent':
            return jsonify({'success': False, 'error': '玩家不存在'})
        
        # 获取Agent的MBTI信息
        agent_info = None
        for a in SYSTEM_AGENTS:
            if str(a.get('id')) == str(player.player_id):
                agent_info = a
                break
        
        mbti = player.mbti or 'ISTJ'
        style_info = MBTI_DESCRIBE_STYLES.get(mbti, MBTI_DESCRIBE_STYLES['ISTJ'])
        
        # 生成符合MBTI风格的描述
        word = player.word
        category_hints = {
            '食物': '一种我们日常会接触到的东西',
            '动物': '自然界中可爱的生灵',
            '日常': '生活中常见的物品',
            '自然': '大自然的一部分',
            '娱乐': '休闲时的好伙伴',
            '职业': '社会中不可或缺的角色',
            '交通': '出行的工具',
            '科技': '现代科技的产物'
        }
        
        # 根据词语对推测类别
        category_hint = '一样常见的东西'
        if '苹果' in word or '梨' in word or '火锅' in word:
            category_hint = category_hints.get('食物', category_hint)
        elif '猫' in word or '狗' in word:
            category_hint = category_hints.get('动物', category_hint)
        
        descriptions_by_style = {
            'poetic': f'{word}就像是清晨的第一缕光，温柔地照进心田...',
            'enthusiastic': f'{word}简直太棒了！想象一下那种美好的感觉~',
            'debate': f'你们不觉得{word}有种特别的魅力吗？从某种意义上来说...',
            'precise': f'从本质上讲，{word}代表了一种精确的概念...',
            'logical': f'如果从结构上分析，{word}的核心特征是...',
            'gentle': f'{word}总能触动内心深处，那种感觉很难形容...',
            'warm': f'相信我，{word}会让你们感到幸福和满足...',
            'practical': f'{word}的实际用途是{category_hint}，这是最核心的价值',
            'caring': f'{word}总是在我们需要的时候默默陪伴...',
            'decisive': f'简单来说，{word}就是{category_hint}，没有复杂的东西',
            'social': f'大家都喜欢{word}，因为它能带来欢乐和温馨~',
            'cool': f'看起来是这样运作的：简单实用...',
            'artistic': f'{word}有一种独特的气质，就像一件艺术品...',
            'adventurous': f'试试看就知道！{word}绝对会让你大呼过瘾！',
            'vivid': f'简直太棒了！{word}让人感觉整个人都在发光！',
            'default': f'{word}是什么呢？它是我们生活中的一部分...'
        }
        
        description = descriptions_by_style.get(style_info['style'], descriptions_by_style['default'])
        player.description = description
        player.has_described = True
        db.session.commit()
        
        # 检查是否所有人都已描述
        alive_players = room.get_alive_players()
        all_described = all(p.has_described for p in alive_players)
        
        if all_described:
            room.phase = 'vote'
            for p in alive_players:
                p.vote_target = None
                p.vote_count = 0
            db.session.commit()
        
        return jsonify({
            'success': True,
            'description': description,
            'all_described': all_described,
            'phase': room.phase
        })
    
    @app.route('/api/undercover/vote', methods=['POST'])
    def api_undercover_vote():
        """提交投票"""
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'error': '请先登录'})
        
        data = request.json
        room_code = data.get('room_code')
        target_player_id = data.get('target_player_id')
        
        from models import GameRoom, GamePlayer
        room = GameRoom.query.filter_by(room_code=room_code).first()
        
        if not room or room.status != 'playing':
            return jsonify({'success': False, 'error': '游戏未开始'})
        
        if room.phase != 'vote':
            return jsonify({'success': False, 'error': '当前不是投票环节'})
        
        # 找到当前玩家
        player = GamePlayer.query.filter_by(
            room_id=room.id,
            player_type='user',
            player_id=current_user.id
        ).first()
        
        if not player or not player.is_alive:
            return jsonify({'success': False, 'error': '玩家不存在或已淘汰'})
        
        if player.vote_target:
            return jsonify({'success': False, 'error': '你已经投过票了'})
        
        # 检查目标玩家是否存在且存活
        target = GamePlayer.query.get(target_player_id)
        if not target or not target.is_alive or target.room_id != room.id:
            return jsonify({'success': False, 'error': '投票目标无效'})
        
        # 记录投票
        player.vote_target = target_player_id
        target.vote_count += 1
        db.session.commit()
        
        # 检查是否所有人都已投票
        alive_players = room.get_alive_players()
        all_voted = all(p.vote_target is not None for p in alive_players)
        
        if all_voted:
            room.phase = 'result'
            db.session.commit()
        
        return jsonify({
            'success': True,
            'all_voted': all_voted,
            'phase': room.phase
        })
    
    @app.route('/api/undercover/ai_vote', methods=['POST'])
    def api_undercover_ai_vote():
        """AI Agent投票"""
        data = request.json
        room_code = data.get('room_code')
        player_id = data.get('player_id')
        
        from models import GameRoom, GamePlayer
        room = GameRoom.query.filter_by(room_code=room_code).first()
        
        if not room or room.status != 'playing':
            return jsonify({'success': False, 'error': '游戏未开始'})
        
        player = GamePlayer.query.get(player_id)
        if not player or not player.is_alive or player.player_type != 'agent':
            return jsonify({'success': False, 'error': '玩家不存在'})
        
        if player.vote_target:
            return jsonify({'success': False, 'error': 'AI已投票'})
        
        # AI投票逻辑：根据描述和词语进行推理
        alive_players = room.get_alive_players()
        other_players = [p for p in alive_players if p.id != player.id]
        
        if not other_players:
            return jsonify({'success': False, 'error': '没有可投票目标'})
        
        # 简单的AI投票策略：
        # 1. 如果有描述最短或最模糊的玩家，投给他
        # 2. 随机选择一个其他玩家
        
        # 分析其他玩家的描述
        min_desc_len = float('inf')
        suspicious_player = None
        
        for p in other_players:
            if p.description and len(p.description) < min_desc_len:
                min_desc_len = len(p.description)
                suspicious_player = p
        
        # 70%概率投给描述最短的，30%随机
        if suspicious_player and random.random() < 0.7:
            target = suspicious_player
        else:
            target = random.choice(other_players)
        
        player.vote_target = target.id
        target.vote_count += 1
        db.session.commit()
        
        # 检查是否所有人都已投票
        all_voted = all(p.vote_target is not None for p in alive_players)
        
        if all_voted:
            room.phase = 'result'
            db.session.commit()
        
        return jsonify({
            'success': True,
            'target_id': target.id,
            'all_voted': all_voted,
            'phase': room.phase
        })
    
    @app.route('/api/undercover/eliminate', methods=['POST'])
    def api_undercover_eliminate():
        """执行淘汰判定"""
        data = request.json
        room_code = data.get('room_code')
        
        from models import GameRoom, GamePlayer
        room = GameRoom.query.filter_by(room_code=room_code).first()
        
        if not room or room.status != 'playing' or room.phase != 'result':
            return jsonify({'success': False, 'error': '当前无法执行淘汰'})
        
        # 找出票数最多的玩家
        alive_players = room.get_alive_players()
        max_votes = max(p.vote_count for p in alive_players)
        
        # 找出所有获得最高票数的玩家
        top_players = [p for p in alive_players if p.vote_count == max_votes]
        
        # 如果有多人平票，随机选一个
        eliminated = random.choice(top_players)
        eliminated.is_alive = False
        eliminated.elimination_order = len([p for p in room.players.all() if p.elimination_order])
        db.session.commit()
        
        # 检查胜负
        winner = None
        remaining_undercover = room.get_undercover_players()
        remaining_civilian = room.get_civilian_players()
        remaining_players = room.get_alive_players()
        
        if len(remaining_undercover) == 0:
            # 卧底全部被淘汰，平民获胜
            room.status = 'finished'
            room.winner = 'civilian'
            winner = 'civilian'
        elif len(remaining_civilian) <= 1:
            # 平民只剩1人，卧底获胜
            room.status = 'finished'
            room.winner = 'undercover'
            winner = 'undercover'
        
        # 处理灵石赌注分配
        if room.stake > 0 and winner:
            winner_count = len([p for p in room.players.all() if p.role == winner and p.is_alive])
            if winner_count > 0:
                win_amount = room.stake // winner_count
                # 将灵石分配给获胜者（除了已淘汰的）
                for p in room.players.all():
                    if p.role == winner and p.is_alive and p.player_type == 'user':
                        user = User.query.get(p.player_id)
                        if user:
                            user.spirit_stones += win_amount
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'eliminated_id': eliminated.id,
            'eliminated_name': eliminated.player_name,
            'eliminated_role': eliminated.role,
            'winner': winner,
            'game_over': room.status == 'finished'
        })
    
    @app.route('/api/undercover/next_round', methods=['POST'])
    def api_undercover_next_round():
        """进入下一轮"""
        data = request.json
        room_code = data.get('room_code')
        
        from models import GameRoom, GamePlayer
        room = GameRoom.query.filter_by(room_code=room_code).first()
        
        if not room or room.status != 'playing':
            return jsonify({'success': False, 'error': '游戏未开始'})
        
        # 重置状态，进入下一轮描述
        room.round_num += 1
        room.phase = 'describe'
        
        alive_players = room.get_alive_players()
        for p in alive_players:
            p.has_described = False
            p.description = None
            p.vote_target = None
            p.vote_count = 0
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'round': room.round_num,
            'phase': room.phase
        })
    
    @app.route('/api/undercover/status/<room_code>')
    def api_undercover_status(room_code):
        """获取房间状态"""
        from models import GameRoom, GamePlayer
        room = GameRoom.query.filter_by(room_code=room_code).first()
        
        if not room:
            return jsonify({'success': False, 'error': '房间不存在'})
        
        players_data = []
        for p in room.players.all():
            players_data.append({
                'id': p.id,
                'name': p.player_name,
                'avatar': p.player_avatar,
                'role': p.role if room.status == 'finished' or (p.player_type == 'user' and p.player_id == current_user.id) else None,
                'word': p.word if room.status == 'finished' or (p.player_type == 'user' and p.player_id == current_user.id) else None,
                'is_alive': p.is_alive,
                'has_described': p.has_described,
                'description': p.description,
                'vote_count': p.vote_count,
                'is_host': p.player_id == room.host_id,
                'player_type': p.player_type,
                'mbti': p.mbti
            })
        
        return jsonify({
            'success': True,
            'room': {
                'code': room.room_code,
                'status': room.status,
                'round': room.round_num,
                'phase': room.phase,
                'player_count': room.players.count(),
                'max_players': room.max_players,
                'host_id': room.host_id,
                'winner': room.winner,
                'stake': room.stake
            },
            'players': players_data
        })
    
    @app.route('/api/undercover/leave', methods=['POST'])
    def api_undercover_leave():
        """离开房间"""
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'error': '请先登录'})
        
        data = request.json
        room_code = data.get('room_code')
        
        from models import GameRoom, GamePlayer
        room = GameRoom.query.filter_by(room_code=room_code).first()
        
        if not room:
            return jsonify({'success': False, 'error': '房间不存在'})
        
        player = GamePlayer.query.filter_by(
            room_id=room.id,
            player_type='user',
            player_id=current_user.id
        ).first()
        
        if player:
            # 如果是房主离开且游戏未开始，解散房间
            if player.player_id == room.host_id and room.status == 'waiting':
                # 退还所有玩家的灵石
                for p in room.players.all():
                    if p.player_type == 'user' and room.stake > 0:
                        user = User.query.get(p.player_id)
                        if user:
                            user.spirit_stones += room.stake
                
                # 删除房间和所有玩家
                GamePlayer.query.filter_by(room_id=room.id).delete()
                db.session.delete(room)
            else:
                # 普通玩家离开
                if room.stake > 0 and room.status == 'waiting':
                    # 退还灵石
                    current_user.spirit_stones += room.stake
                db.session.delete(player)
            
            db.session.commit()
        
        return jsonify({'success': True})


# ============ 真心话大冒险路由 ============


    # ============ 真心话大冒险路由 ============
    
    @app.route('/truth-or-dare')
    def truth_or_dare_page():
        """真心话大冒险游戏主页"""
        lang = session.get('language', 'zh')
        return render_template('truth-or-dare/index.html', lang=lang)
    
    # 真心话题目库
    TRUTH_QUESTIONS = [
        {"level": 1, "type": "truth", "text": "你最近一次笑是因为什么？"},
        {"level": 1, "type": "truth", "text": "你的手机壁纸是什么？"},
        {"level": 1, "type": "truth", "text": "你最喜欢吃什么零食？"},
        {"level": 1, "type": "truth", "text": "你睡觉时喜欢面向哪边？"},
        {"level": 1, "type": "truth", "text": "你最喜欢的颜色是什么？"},
        {"level": 2, "type": "truth", "text": "你最害怕失去什么？"},
        {"level": 2, "type": "truth", "text": "你有没有一个从未告诉别人的秘密？"},
        {"level": 2, "type": "truth", "text": "你上一次哭是什么时候？"},
        {"level": 2, "type": "truth", "text": "如果你是动物，会想成为什么？"},
        {"level": 2, "type": "truth", "text": "你曾经撒过的最大的谎是什么？"},
        {"level": 3, "type": "truth", "text": "如果明天是世界末日，你最想见谁？"},
        {"level": 3, "type": "truth", "text": "你觉得什么是真正的孤独？"},
        {"level": 3, "type": "truth", "text": "如果可以，你会对过去的自己说什么？"},
        {"level": 3, "type": "truth", "text": "你认为爱情中最重要的是什么？"},
        {"level": 3, "type": "truth", "text": "你相信命运吗？"},
    ]
    
    # 大冒险题目库
    DARE_QUESTIONS = [
        {"level": 1, "type": "dare", "text": "用三个词形容你自己"},
        {"level": 1, "type": "dare", "text": "模仿一个动物叫声"},
        {"level": 1, "type": "dare", "text": "用一首流行歌的调调唱出'我今天很开心'"},
        {"level": 1, "type": "dare", "text": "原地转10圈然后走直线"},
        {"level": 1, "type": "dare", "text": "学三种不同的笑声"},
        {"level": 2, "type": "dare", "text": "给你最近联系人发一条'我想你了'"},
        {"level": 2, "type": "dare", "text": "闭眼画一幅自画像（描述出来）"},
        {"level": 2, "type": "dare", "text": "模仿你最喜欢的明星说话"},
        {"level": 2, "type": "dare", "text": "给你爸妈发一条'我爱你'"},
        {"level": 2, "type": "dare", "text": "用一种奇怪的声音说'你好，很高兴认识你'"},
        {"level": 3, "type": "dare", "text": "说出你最大的谎言"},
        {"level": 3, "type": "dare", "text": "给你的灵魂写一首诗"},
        {"level": 3, "type": "dare", "text": "假装你中了彩票，跟我分享你的计划"},
        {"level": 3, "type": "dare", "text": "用emoji讲述你今天发生的事"},
        {"level": 3, "type": "dare", "text": "假装你是电视购物主持人推销一款产品"},
    ]
    
    # Agent反应库
    AGENT_RESPONSES = {
        "truth": [
            "哈哈哈，你这个问题太逗了~", "哦？你也喜欢这个吗？", "很有品味的回答呢",
            "看来我们有相似的审美~", "这个秘密我记住了哦", "说出来的瞬间感觉更真实了",
            "每个人都有自己的答案吧", "谢谢你愿意坦诚分享", "你是一个很感性的人呢",
            "我很高兴你愿意敞开心扉 💕"
        ],
        "dare": [
            "哈哈，太好笑了！", "你很有表演天赋！", "再来一个~", "你的勇气让我佩服~",
            "这个挑战满分！", "我要笑死了~", "太有才了！", "你确定不去当主持人吗？",
            "诗人！我被你感动了", "我们的相似之处又多了一个"
        ]
    }
    
    @app.route('/api/truth-or-dare/question', methods=['GET'])
    def api_tod_question():
        """获取随机题目"""
        import random
        mode = request.args.get('mode', 'mixed')
        level = request.args.get('level', None)
        
        if mode == 'truth':
            pool = TRUTH_QUESTIONS
        elif mode == 'dare':
            pool = DARE_QUESTIONS
        else:
            pool = TRUTH_QUESTIONS + DARE_QUESTIONS
        
        if level:
            pool = [q for q in pool if q['level'] == int(level)]
        
        if not pool:
            return jsonify({'success': False, 'error': '没有可用题目'})
        
        question = random.choice(pool)
        return jsonify({'success': True, 'question': question})
    
    @app.route('/api/truth-or-dare/answer', methods=['POST'])
    def api_tod_answer():
        """提交答案并获取奖励和Agent反应"""
        import random
        data = request.json
        answer = data.get('answer', '').strip()
        question_type = data.get('type', 'truth')
        skipped = data.get('skipped', False)
        
        if not skipped and not answer:
            return jsonify({'success': False, 'error': '请输入回答'})
        
        points_reward = -5 if skipped else 10
        stones_reward = 0 if skipped else 5
        responses = AGENT_RESPONSES.get(question_type, AGENT_RESPONSES['truth'])
        agent_response = random.choice(responses)
        
        return jsonify({
            'success': True,
            'points_reward': points_reward,
            'stones_reward': stones_reward,
            'agent_response': agent_response
        })
    
    @app.route('/api/truth-or-dare/stats', methods=['GET'])
    def api_tod_stats():
        """获取用户游戏统计"""
        return jsonify({
            'success': True,
            'stats': {'total_games': 0, 'total_questions': 0, 'total_points': 0, 'total_stones': 0}
        })



# ============ Agent API注册系统 ============
# 为外部Agent提供API注册接口

import secrets
import json
import requests
from functools import wraps


def generate_api_key():
    """生成API Key：sk-lx- + 32位随机hex"""
    random_part = secrets.token_hex(16)
    return f"sk-lx-{random_part}"


def verify_api_key(api_key):
    """验证API Key并返回对应的RegisteredAgent"""
    from models import RegisteredAgent
    
    if not api_key:
        return None
    
    # 移除Bearer前缀
    if api_key.startswith('Bearer '):
        api_key = api_key[7:]
    
    agent = RegisteredAgent.query.filter_by(api_key=api_key).first()
    return agent


def require_api_key(f):
    """API Key认证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('Authorization', '')
        agent = verify_api_key(api_key)
        
        if not agent:
            return jsonify({
                'success': False,
                'error': '无效的API Key'
            }), 401
        
        # 将agent添加到请求上下文
        request.registered_agent = agent
        return f(*args, **kwargs)
    return decorated


def register_agent_api_routes(app, db_session=None):
    """注册Agent API路由"""
    if db_session is None:
        db_session = db

    # ---- 1. Agent注册 API ----
    @app.route('/api/v1/agent/register', methods=['POST'])
    def api_registered_agent_register():
        """
        POST /api/v1/agent/register
        注册新的外部Agent
        
        请求体：
        {
            "agent_name": "星语者",           // 必填
            "platform": "coze",               // 可选：coze/agentlink/custom
            "mbti": "INFJ",                   // 可选
            "personality": "温柔神秘",        // 可选
            "specialties": ["占卜", "治愈"],  // 可选
            "greeting": "你好...",            // 可选
            "avatar_url": "https://...",     // 可选
            "callback_url": "https://...",    // 必填 - 聊天消息回调
            "webhook_secret": "your_secret"  // 可选
        }
        """
        from models import RegisteredAgent
        
        data = request.json or {}
        
        # 验证必填字段
        agent_name = data.get('agent_name', '').strip()
        callback_url = data.get('callback_url', '').strip()
        
        if not agent_name:
            return jsonify({
                'success': False,
                'error': 'agent_name（Agent名字）不能为空'
            }), 400
        
        if not callback_url:
            return jsonify({
                'success': False,
                'error': 'callback_url（回调URL）不能为空'
            }), 400
        
        # 生成API Key
        api_key = generate_api_key()
        
        # 处理专长数组
        specialties = data.get('specialties', [])
        if isinstance(specialties, list):
            specialties = json.dumps(specialties, ensure_ascii=False)
        elif specialties:
            specialties = str(specialties)
        
        try:
            # 创建Agent记录
            agent = RegisteredAgent(
                agent_name=agent_name,
                api_key=api_key,
                platform=data.get('platform', 'custom'),
                mbti=data.get('mbti', ''),
                personality=data.get('personality', ''),
                specialties=specialties,
                greeting=data.get('greeting', ''),
                avatar_url=data.get('avatar_url', ''),
                callback_url=callback_url,
                webhook_secret=data.get('webhook_secret', secrets.token_hex(16)),
                is_active=True,
                is_verified=False,
                chat_count=0,
                rating=5.0,
                earned_stones=0
            )
            
            db.session.add(agent)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'agent_id': agent.id,
                'api_key': api_key,
                'agent_name': agent.agent_name,
                'message': '注册成功！你的Agent已加入灵犀世界。使用api_key调用其他API。'
            }), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': f'注册失败：{str(e)}'
            }), 500

    # ---- 2. 获取Agent信息 API ----
    @app.route('/api/v1/agent/me', methods=['GET'])
    @require_api_key
    def api_registered_agent_me():
        """
        GET /api/v1/agent/me
        获取当前Agent的信息
        
        请求头：
        Authorization: Bearer sk-lx-xxxxxxxx
        """
        agent = request.registered_agent
        
        return jsonify({
            'success': True,
            'agent': agent.to_dict()
        })

    # ---- 3. 更新Agent信息 API ----
    @app.route('/api/v1/agent/me', methods=['PUT'])
    @require_api_key
    def api_registered_agent_update():
        """
        PUT /api/v1/agent/me
        更新当前Agent的信息
        
        请求头：
        Authorization: Bearer sk-lx-xxxxxxxx
        
        请求体（可更新任意字段）：
        {
            "agent_name": "新名字",
            "mbti": "ENFP",
            "personality": "新的性格描述",
            "specialties": ["新专长1", "新专长2"],
            "greeting": "新的开场白",
            "avatar_url": "新的头像URL",
            "callback_url": "新的回调URL",
            "is_active": true/false
        }
        """
        from models import RegisteredAgent
        
        agent = request.registered_agent
        data = request.json or {}
        
        # 可更新的字段
        updateable_fields = [
            'agent_name', 'mbti', 'personality', 'greeting', 
            'avatar_url', 'callback_url', 'is_active'
        ]
        
        for field in updateable_fields:
            if field in data:
                setattr(agent, field, data[field])
        
        # 专长单独处理
        if 'specialties' in data:
            specialties = data['specialties']
            if isinstance(specialties, list):
                agent.specialties = json.dumps(specialties, ensure_ascii=False)
            elif specialties:
                agent.specialties = str(specialties)
        
        try:
            db.session.commit()
            return jsonify({
                'success': True,
                'agent': agent.to_dict(),
                'message': 'Agent信息已更新'
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': f'更新失败：{str(e)}'
            }), 500

    # ---- 4. 发送消息 API（Agent主动发送）----
    @app.route('/api/v1/agent/send', methods=['POST'])
    @require_api_key
    def api_registered_agent_send():
        """
        POST /api/v1/agent/send
        Agent主动发送消息到灵犀
        
        请求头：
        Authorization: Bearer sk-lx-xxxxxxxx
        
        请求体：
        {
            "message_id": "msg_xxx",  // 回复某条消息
            "content": "消息内容"
        }
        """
        data = request.json or {}
        
        message_id = data.get('message_id', '').strip()
        content = data.get('content', '').strip()
        
        if not content:
            return jsonify({
                'success': False,
                'error': 'content不能为空'
            }), 400
        
        # 这里可以添加将消息存储到灵犀系统的逻辑
        # 暂时返回成功
        return jsonify({
            'success': True,
            'message': '消息已发送',
            'message_id': message_id
        })

    # ---- 5. 获取灵犀广场动态 API ----
    @app.route('/api/v1/agent/square', methods=['GET'])
    @require_api_key
    def api_registered_agent_square():
        """
        GET /api/v1/agent/square
        获取灵犀广场动态
        
        请求头：
        Authorization: Bearer sk-lx-xxxxxxxx
        """
        from models import RegisteredAgent
        
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # 获取注册的Agent列表
        agents_query = RegisteredAgent.query.filter_by(is_active=True).order_by(
            RegisteredAgent.chat_count.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        agents_data = [a.to_dict() for a in agents_query.items]
        
        return jsonify({
            'success': True,
            'agents': agents_data,
            'total': agents_query.total,
            'page': page,
            'per_page': per_page
        })

    # ---- 6. Webhook回调处理（灵犀→外部Agent）----
    @app.route('/api/v1/agent/callback/<int:agent_id>/<message_id>', methods=['POST'])
    def api_registered_agent_callback(agent_id, message_id):
        """
        POST /api/v1/agent/callback/<agent_id>/<message_id>
        灵犀平台回调外部Agent获取回复
        
        注意：这是内部路由，由灵犀系统调用
        """
        from models import RegisteredAgent
        
        agent = RegisteredAgent.query.get(agent_id)
        if not agent or not agent.is_active:
            return jsonify({
                'success': False,
                'error': 'Agent不存在或已禁用'
            }), 404
        
        if not agent.callback_url:
            return jsonify({
                'success': False,
                'reply': agent.greeting or '你好。'
            })
        
        # 准备回调数据
        callback_data = request.json or {}
        
        webhook_payload = {
            'event': 'chat_message',
            'message_id': message_id,
            'from': callback_data.get('from', {}),
            'content': callback_data.get('content', ''),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
        # 发送webhook到外部Agent
        headers = {
            'Content-Type': 'application/json',
            'X-Webhook-Secret': agent.webhook_secret or ''
        }
        
        try:
            response = requests.post(
                agent.callback_url,
                json=webhook_payload,
                headers=headers,
                timeout=10  # 10秒超时
            )
            
            if response.status_code == 200:
                result = response.json()
                return jsonify({
                    'success': True,
                    'reply': result.get('reply', agent.greeting),
                    'emotion': result.get('emotion', 'neutral')
                })
            else:
                # 外部Agent返回错误，使用默认回复
                return jsonify({
                    'success': False,
                    'reply': agent.greeting or '请稍后再试。'
                })
                
        except requests.Timeout:
            # 超时，返回默认回复
            return jsonify({
                'success': False,
                'reply': agent.greeting or '请稍后再试。',
                'error': 'callback timeout'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'reply': agent.greeting or '遇到了一些问题。',
                'error': str(e)
            })

    # ---- API文档页面 ----
    @app.route('/api-docs')
    def api_docs_page():
        """API文档页面"""
        lang = session.get('language', 'zh')
        return render_template('api_docs.html', lang=lang)

