"""
分享卡片 + 邀请码系统 - app.py 路由添加脚本
将以下代码追加到 app.py 末尾
"""
import random
import string
from datetime import datetime

# ============ 辅助函数 ============

def generate_invite_code():
    """生成8位邀请码"""
    chars = string.ascii_uppercase + string.digits
    return 'SL' + ''.join(random.choices(chars, k=6))


# ============ 分享卡片路由 ============

@app.route('/share/card/<card_type>')
@login_required
def share_card_page(card_type):
    """分享卡片页面"""
    lang = session.get('lang', 'zh')
    
    # 根据类型获取数据
    card_data = {
        'card_type': '测试结果',
        'main_result': '???',
        'sub_result': '',
        'description': '探索命运，发现自我',
        'tags': []
    }
    
    if card_type == 'mbti':
        # 获取最新MBTI结果
        from models import Divination
        div = Divination.query.filter_by(
            user_id=current_user.id,
            divination_type='mbti'
        ).order_by(Divination.created_at.desc()).first()
        
        if div:
            card_data = {
                'card_type': 'MBTI 测试',
                'main_result': div.result_data.get('mbti_type', '???') if isinstance(div.result_data, dict) else '???',
                'sub_result': div.result_data.get('mbti_name', '') if isinstance(div.result_data, dict) else '',
                'description': div.result_data.get('description', '')[:100] if isinstance(div.result_data, dict) else '',
                'tags': ['MBTI', '性格测试', 'SoulLink']
            }
    
    elif card_type == 'divination':
        # 获取最新占卜结果
        from models import Divination
        div = Divination.query.filter_by(
            user_id=current_user.id
        ).filter(Divination.divination_type.in_(['tarot', 'love', 'horoscope', 'bazi'])
        ).order_by(Divination.created_at.desc()).first()
        
        if div:
            card_data = {
                'card_type': '占卜结果',
                'main_result': div.result_title[:20] if div.result_title else '命运之谜',
                'sub_result': '',
                'description': div.result_content[:80] if div.result_content else '命运的齿轮开始转动...',
                'tags': ['占卜', '命运', 'SoulLink']
            }
    
    elif card_type == 'zodiac':
        # 获取星座配对结果
        zodiac_data = session.get('zodiac_match_result')
        if zodiac_data:
            card_data = {
                'card_type': '星座配对',
                'main_result': zodiac_data.get('match_score', '80') + '%',
                'sub_result': zodiac_data.get('match_title', '契合度高'),
                'description': zodiac_data.get('match_desc', '你们之间有着奇妙的缘分...')[:100],
                'tags': ['星座', '配对', '缘分', 'SoulLink']
            }
    
    return render_template('share/share_card.html',
        lang=lang,
        card_data=card_data
    )


@app.route('/api/share/generate-card', methods=['POST'])
@login_required
def generate_share_card():
    """生成分享卡片数据"""
    data = request.get_json()
    card_type = data.get('type', 'mbti')
    
    result_data = {
        'card_type': '测试结果',
        'main_result': '???',
        'sub_result': '',
        'description': '探索命运，发现自我',
        'tags': ['SoulLink']
    }
    
    if card_type == 'mbti':
        from models import Divination
        div = Divination.query.filter_by(
            user_id=current_user.id,
            divination_type='mbti'
        ).order_by(Divination.created_at.desc()).first()
        
        if div and isinstance(div.result_data, dict):
            result_data = {
                'card_type': 'MBTI 测试',
                'main_result': div.result_data.get('mbti_type', '???'),
                'sub_result': div.result_data.get('mbti_name', ''),
                'description': div.result_data.get('description', '')[:100],
                'tags': ['MBTI', '性格测试', 'SoulLink']
            }
    
    return jsonify({'success': True, 'data': result_data})


# ============ 邀请码系统路由 ============

@app.route('/invite')
@login_required
def invite_page():
    """邀请好友页面"""
    lang = session.get('lang', 'zh')
    user = User.query.get(current_user.id)
    
    # 确保用户有邀请码
    if not user.invite_code:
        user.invite_code = generate_invite_code()
        db.session.commit()
    
    # 生成邀请链接
    share_url = f"https://soullink-cnz2.onrender.com/auth/register?invite={user.invite_code}"
    
    # 获取邀请记录
    from models import Invitation
    invitations = Invitation.query.filter_by(inviter_id=user.id).order_by(
        Invitation.created_at.desc()
    ).limit(20).all()
    
    # 统计数据
    total_invites = len(invitations)
    total_reward = sum(inv.reward for inv in invitations)
    
    # 获取排行榜
    leaderboard = db.session.query(
        User.username,
        db.func.count(Invitation.id).label('count')
    ).join(Invitation, Invitation.inviter_id == User.id
    ).group_by(User.id, User.username
    ).order_by(db.desc('count')
    ).limit(10).all()
    
    return render_template('share/invite.html',
        lang=lang,
        invite_code=user.invite_code,
        share_url=share_url,
        invitations=invitations,
        total_invites=total_invites,
        total_reward=total_reward,
        leaderboard=[{'username': u, 'count': c} for u, c in leaderboard]
    )


@app.route('/api/invite/stats')
@login_required
def invite_stats():
    """获取邀请统计"""
    from models import Invitation
    
    total_invites = Invitation.query.filter_by(inviter_id=current_user.id).count()
    total_reward = db.session.query(db.func.sum(Invitation.reward)
    ).filter_by(inviter_id=current_user.id).scalar() or 0
    
    return jsonify({
        'success': True,
        'total_invites': total_invites,
        'total_reward': total_reward
    })


# ============ 注册时邀请码处理 ============

@app.before_app_request
def handle_invite_code():
    """处理邀请码 - 在用户注册后自动添加灵石"""
    if 'pending_invite_code' in session:
        invite_code = session.pop('pending_invite_code')
        
        if current_user.is_authenticated:
            inviter = User.query.filter_by(invite_code=invite_code).first()
            
            if inviter and inviter.id != current_user.id:
                # 检查是否已经邀请过
                from models import Invitation
                existing = Invitation.query.filter_by(
                    inviter_id=inviter.id,
                    invitee_id=current_user.id
                ).first()
                
                if not existing:
                    # 创建邀请记录
                    invitation = Invitation(
                        inviter_id=inviter.id,
                        invitee_id=current_user.id,
                        reward=50
                    )
                    db.session.add(invitation)
                    
                    # 给邀请人加50灵石
                    inviter.spirit_stones += 50
                    
                    # 给被邀请人加50灵石
                    current_user.spirit_stones += 50
                    
                    db.session.commit()


# ============ 数据库模型（如果不存在） ============

class Invitation(db.Model):
    """邀请记录模型"""
    __tablename__ = 'invitations'
    
    id = db.Column(db.Integer, primary_key=True)
    inviter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    invitee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reward = db.Column(db.Integer, default=50)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    inviter = db.relationship('User', foreign_keys=[inviter_id], backref='invitations_sent')
    invitee = db.relationship('User', foreign_keys=[invitee_id], backref='invitations_received')

