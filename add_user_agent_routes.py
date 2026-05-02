#!/usr/bin/env python3
"""添加UserAgent相关路由到routes_supplementary.py"""

import os

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# 读取routes_supplementary.py
with open('routes_supplementary.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 检查是否已存在UserAgent路由
if 'user_agent_create_api' in content:
    print("UserAgent路由已存在，跳过添加")
    exit(0)

# 新的路由代码
new_routes = '''

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
        
        return render_template('user_agent_profile.html', 
                             agent=agent,
                             creator=creator,
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

'''

# 在register_lingstone_routes函数之前添加
insert_point = '\ndef register_lingstone_routes(app, db_session=None):'
if insert_point in content:
    content = content.replace(insert_point, new_routes + insert_point)
    with open('routes_supplementary.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("UserAgent路由添加成功！")
else:
    print("未找到插入点，尝试在文件末尾添加")
    # 尝试在文件末尾添加
    content = content + new_routes
    with open('routes_supplementary.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("UserAgent路由已添加到文件末尾")
