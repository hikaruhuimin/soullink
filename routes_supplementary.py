# 补充路由和API端点 - 灵石经济系统 + 好友系统

from flask import request, jsonify, session, render_template, redirect, url_for
from flask_login import current_user
from functools import wraps
from datetime import datetime
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


def register_lingstone_routes(app, db_session=None):
    """灵石经济路由 - 占位符，路由已在register_supplementary_routes中注册"""
    pass
