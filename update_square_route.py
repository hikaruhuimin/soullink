#!/usr/bin/env python3
"""更新灵犀广场路由"""

import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# 读取routes_supplementary.py
with open('routes_supplementary.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 旧的agents_square_page函数
old_function = '''    # ============ Agent广场 ============
    @app.route('/agents')
    def agents_square_page():
        """Agent广场"""
        from models import SYSTEM_AGENTS
        
        lang = session.get('language', 'zh')
        system_agents = SYSTEM_AGENTS
        female_agents = [a for a in system_agents if a.get('gender') == 'female']
        male_agents = [a for a in system_agents if a.get('gender') != 'male']
        
        # 添加mood_zh
        mood_zh_map = {
            'happy': '开心', 'sassy': '傲娇', 'mysterious': '神秘', 
            'excited': '兴奋', 'commanding': '霸气', 'laughing': '欢笑',
            'energetic': '元气', 'calm': '平静'
        }
        for agents in [female_agents, male_agents]:
            for agent in agents:
                agent['mood_zh'] = mood_zh_map.get(agent.get('mood', 'happy'), '开心')
        
        return render_template('agents_square.html', 
                             lang=lang, 
                             system_agents=system_agents,
                             female_agents=female_agents, 
                             male_agents=male_agents)'''

# 新的agents_square_page函数
new_function = '''    # ============ 灵犀广场 ============
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
                             mood_colors=mood_colors)'''

if old_function in content:
    content = content.replace(old_function, new_function)
    with open('routes_supplementary.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("agents_square_page路由更新成功！")
else:
    print("未找到旧函数，可能是已经更新过了")
