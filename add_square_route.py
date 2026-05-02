#!/usr/bin/env python3
"""添加Agent广场路由到routes_supplementary.py"""

import os

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# 读取routes_supplementary.py
with open('routes_supplementary.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 检查是否已存在广场路由
if 'agents_square_page_for_user' in content:
    print("Agent广场路由已存在，跳过添加")
    exit(0)

# 新的广场路由代码
new_routes = '''

    # ============ Agent广场页面 ============
    @app.route('/agents')
    def agents_square_main():
        """灵犀广场 - 展示系统Agent和用户Agent"""
        from models import SYSTEM_AGENTS, UserAgent
        
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

'''

# 在register_supplementary_routes函数开头添加（在第一个@app.route之前）
# 找到第一个@app.route的位置
import re
first_route_match = re.search(r'    @app\.route', content)
if first_route_match:
    insert_pos = first_route_match.start()
    content = content[:insert_pos] + new_routes + content[insert_pos:]
    with open('routes_supplementary.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Agent广场路由添加成功！")
else:
    print("未找到插入点")
