# 补充路由和API端点 - 好友系统

from flask import request, jsonify, session, render_template, redirect, url_for
from flask_login import current_user
from functools import wraps
from datetime import datetime
from models import db

# ============ 好友系统路由 ============

def register_supplementary_routes(app):
    """注册补充路由 - 好友系统"""
    
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
