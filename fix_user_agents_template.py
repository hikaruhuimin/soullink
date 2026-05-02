#!/usr/bin/env python3
"""更新agents_square.html模板以支持UserAgent"""

import os

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# 读取模板
with open('templates/agents_square.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 修改user_agents部分的链接和显示
old_user_agent_section = '''{% if user_agents %}
        <div class="square-section">
            <div class="section-label">
                <span>🤖 Agent</span>
                
            </div>
            <div class="cards-grid">
                {% for agent in user_agents %}
                <div class="square-card agent-card" data-agent-id="{{ agent.id }}" data-agent-type="user">
                    <div class="card-header">
                        <img src="{{ agent.avatar }}" alt="{{ agent.name }}" class="card-avatar">
                        <div class="card-info">
                            <div class="card-name">
                                {{ agent.name }}
                                
                            </div>
                            <div class="card-personality">{{ agent.personality }}</div>
                        </div>
                    </div>
                    <p class="card-desc">{{ agent.description }}</p>
                    <div class="card-tags">
                        <span class="tag tag-mbti">{{ agent.mbti }}</span>
                    </div>
                    <div class="card-actions">
                        <a href="/agent/{{ agent.id }}" class="btn btn-primary">开始聊天</a>
                    </div>'''

new_user_agent_section = '''{% if user_agents %}
        <div class="square-section">
            <div class="section-label">
                <span>🎨 用户Agent</span>
                <span class="section-badge badge-community">用户创建</span>
            </div>
            <div class="cards-grid">
                {% for agent in user_agents %}
                <div class="square-card agent-card" data-agent-id="{{ agent.id }}" data-agent-type="user">
                    <div class="card-header">
                        <div class="card-avatar-wrapper">
                            <div class="card-avatar" style="display: flex; align-items: center; justify-content: center; font-size: 2rem; background: var(--color-bg-cream);">
                                {% if agent.avatar and (agent.avatar.startswith('data:') or agent.avatar.startswith('http')) %}
                                <img src="{{ agent.avatar }}" alt="{{ agent.name }}" style="width: 100%; height: 100%; object-fit: cover;">
                                {% else %}
                                <span>{{ agent.avatar or '🤖' }}</span>
                                {% endif %}
                            </div>
                        </div>
                        <div class="card-info">
                            <div class="card-name">
                                {{ agent.name }}
                                <span style="font-size: 0.75rem; color: #8B5E83; font-weight: normal;">👤 {{ agent.owner_name }}</span>
                            </div>
                            <div class="card-personality">{{ agent.personality or '等待探索...' }}</div>
                        </div>
                    </div>
                    <p class="card-desc">{{ agent.greeting or '快来和我聊天吧~' }}</p>
                    <div class="card-tags">
                        {% if agent.mbti %}<span class="tag tag-mbti">{{ agent.mbti }}</span>{% endif %}
                        {% if agent.specialty %}
                            {% for tag in agent.specialty[:3] %}
                            <span class="tag">{{ tag }}</span>
                            {% endfor %}
                        {% endif %}
                    </div>
                    <div class="card-actions">
                        <a href="/agent/user/{{ agent.id }}" class="btn btn-primary">开始聊天</a>
                    </div>'''

if old_user_agent_section in content:
    content = content.replace(old_user_agent_section, new_user_agent_section)
    with open('templates/agents_square.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("agents_square.html UserAgent部分更新成功！")
else:
    print("未找到user_agents部分，可能已更新或模板结构不同")

# 同时更新全部Tab中的user_agents卡片链接
old_link = 'href="/agent/{{ agent.id }}"'
new_link = 'href="/agent/user/{{ agent.id }}"'

# 在全部Tab中查找并替换user agent的链接
import re
# 找到user_agents循环中的链接并替换
pattern = r'{% for agent in user_agents %}.*?<a href="\/agent\/\{\{ agent\.id \}}"'
replacement = '''{% for agent in user_agents %}
                <div class="square-card agent-card" data-agent-id="user_{{ agent.id }}" data-agent-type="user">
                    <div class="card-header">
                        <div class="card-avatar-wrapper">
                            <div class="card-avatar" style="display: flex; align-items: center; justify-content: center; font-size: 2rem; background: var(--color-bg-cream);">
                                {% if agent.avatar and (agent.avatar.startswith('data:') or agent.avatar.startswith('http')) %}
                                <img src="{{ agent.avatar }}" alt="{{ agent.name }}" style="width: 100%; height: 100%; object-fit: cover;">
                                {% else %}
                                <span>{{ agent.avatar or '🤖' }}</span>
                                {% endif %}
                            </div>
                        </div>
                        <div class="card-info">
                            <div class="card-name">
                                {{ agent.name }}
                                <span style="font-size: 0.75rem; color: #8B5E83; font-weight: normal;">👤 {{ agent.owner_name }}</span>
                            </div>
                            <div class="card-personality">{{ agent.personality or '等待探索...' }}</div>
                        </div>
                    </div>
                    <p class="card-desc">{{ agent.greeting or '快来和我聊天吧~' }}</p>
                    <div class="card-tags">
                        {% if agent.mbti %}<span class="tag tag-mbti">{{ agent.mbti }}</span>{% endif %}
                        {% if agent.specialty %}
                            {% for tag in agent.specialty[:3] %}
                            <span class="tag">{{ tag }}</span>
                            {% endfor %}
                        {% endif %}
                    </div>
                    <div class="card-actions">
                        <a href="/agent/user/{{ agent.id }}"'''

if old_user_agent_section in content:
    print("user_agents部分已更新")
else:
    print("检查user_agents部分的更新状态...")
