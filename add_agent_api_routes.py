#!/usr/bin/env python3
"""追加Agent API路由到routes_supplementary.py - 无缩进版本"""

import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
routes_path = os.path.join(script_dir, 'routes_supplementary.py')

# 读取现有内容
with open(routes_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 检查是否已存在
if 'def register_agent_api_routes' in content:
    print("Agent API路由已存在，跳过添加")
    sys.exit(0)

# 定义要追加的路由代码
routes_code = '''


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
    def api_agent_register():
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
    def api_agent_me():
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
    def api_agent_update():
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
    def api_agent_send():
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
    def api_agent_square():
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
    def api_agent_callback(agent_id, message_id):
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
                'reply': agent.greeting or '你好，我是{agent.agent_name}。'
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
                    'reply': agent.greeting or f'你好，我是{agent.agent_name}，请稍后再试。'
                })
                
        except requests.Timeout:
            # 超时，返回默认回复
            return jsonify({
                'success': False,
                'reply': agent.greeting or f'你好，我是{agent.agent_name}，请稍后再试。',
                'error': 'callback timeout'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'reply': agent.greeting or f'你好，我是{agent.agent_name}，遇到了一些问题。',
                'error': str(e)
            })

    # ---- API文档页面 ----
    @app.route('/api-docs')
    def api_docs_page():
        """API文档页面"""
        lang = session.get('language', 'zh')
        return render_template('api_docs.html', lang=lang)


'''

    # 在文件末尾追加
    new_content = content + routes_code
    
    # 写回文件
    with open(routes_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"成功追加Agent API路由到 {routes_path}")


if __name__ == '__main__':
    register_agent_api_routes(None)
