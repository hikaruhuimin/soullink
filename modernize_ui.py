#!/usr/bin/env python3
"""
SoulLink 完整UI现代化改造
- 7个一级菜单导航栏
- 星空宇宙主题背景
- 毛玻璃效果
- 三语翻译
"""

import os

def rewrite_navbar():
    """完全重写导航栏 - 7个菜单"""
    filepath = "templates/base.html"
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # ===== 全新CSS样式 =====
    new_css = '''    <style>
        /* ========== 现代化导航栏 ========== */
        .navbar {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 9999;
            background: rgba(15, 15, 35, 0.85);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(139, 92, 246, 0.15);
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);
        }
        
        .nav-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            height: 68px;
        }
        
        .nav-logo {
            display: flex;
            align-items: center;
            gap: 12px;
            font-family: 'Playfair Display', serif;
            font-size: 1.5rem;
            font-weight: 600;
            color: white;
            text-decoration: none;
            transition: all 0.3s;
        }
        
        .nav-logo:hover {
            transform: translateY(-2px);
        }
        
        .nav-logo-icon {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #8b5cf6, #ec4899);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
            box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4);
        }
        
        .nav-logo-text {
            background: linear-gradient(135deg, #f0abfc, #818cf8, #22d3ee);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .nav-menu {
            display: flex;
            align-items: center;
            gap: 6px;
        }
        
        /* ========== 一级菜单 ========== */
        .nav-item {
            position: relative;
            padding: 12px 18px;
            background: transparent;
            border: none;
            color: rgba(255, 255, 255, 0.8);
            font-size: 0.9rem;
            font-weight: 500;
            cursor: pointer;
            border-radius: 14px;
            transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .nav-item:hover {
            color: white;
            background: rgba(139, 92, 246, 0.2);
            text-shadow: 0 0 20px rgba(139, 92, 246, 0.5);
        }
        
        .nav-item.active {
            color: white;
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.3), rgba(236, 72, 153, 0.2));
            box-shadow: 0 0 20px rgba(139, 92, 246, 0.3);
        }
        
        .nav-item-icon {
            font-size: 1.15rem;
            filter: drop-shadow(0 0 5px currentColor);
        }
        
        .nav-item-arrow {
            font-size: 0.65rem;
            opacity: 0.6;
            transition: all 0.3s;
        }
        
        .nav-item:hover .nav-item-arrow {
            opacity: 1;
            transform: rotate(180deg);
        }
        
        /* ========== 下拉菜单 ========== */
        .nav-dropdown {
            display: none;
            position: absolute;
            top: calc(100% + 12px);
            left: 50%;
            transform: translateX(-50%) translateY(-10px);
            min-width: 240px;
            background: rgba(20, 20, 50, 0.95);
            backdrop-filter: blur(25px);
            -webkit-backdrop-filter: blur(25px);
            border: 1px solid rgba(139, 92, 246, 0.2);
            border-radius: 20px;
            padding: 12px;
            box-shadow: 0 25px 80px rgba(0, 0, 0, 0.4), 0 0 40px rgba(139, 92, 246, 0.15);
            z-index: 10000;
            opacity: 0;
            visibility: hidden;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .nav-item:hover .nav-dropdown {
            display: block;
            opacity: 1;
            visibility: visible;
            transform: translateX(-50%) translateY(0);
        }
        
        .nav-dropdown::before {
            content: '';
            position: absolute;
            top: -10px;
            left: 50%;
            transform: translateX(-50%);
            border: 10px solid transparent;
            border-bottom-color: rgba(139, 92, 246, 0.2);
        }
        
        .nav-dropdown-item {
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 14px 16px;
            color: rgba(255, 255, 255, 0.75);
            font-size: 0.875rem;
            text-decoration: none;
            border-radius: 14px;
            transition: all 0.25s;
        }
        
        .nav-dropdown-item:hover {
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.25), rgba(139, 92, 246, 0.1));
            color: white;
            transform: translateX(6px);
            box-shadow: 0 0 20px rgba(139, 92, 246, 0.2);
        }
        
        .nav-dropdown-item.active {
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.35), rgba(139, 92, 246, 0.2));
            color: white;
            font-weight: 500;
        }
        
        .nav-dropdown-item-icon {
            font-size: 1.3rem;
            width: 36px;
            height: 36px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(139, 92, 246, 0.15);
            border-radius: 10px;
            transition: all 0.25s;
        }
        
        .nav-dropdown-item:hover .nav-dropdown-item-icon {
            background: rgba(139, 92, 246, 0.3);
            transform: scale(1.1);
        }
        
        .nav-dropdown-item-text {
            flex: 1;
        }
        
        .nav-dropdown-item-title {
            font-weight: 500;
            margin-bottom: 3px;
        }
        
        .nav-dropdown-item-desc {
            font-size: 0.75rem;
            color: rgba(255, 255, 255, 0.5);
        }
        
        /* ========== 右侧操作区 ========== */
        .nav-actions {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .nav-lang-dropdown {
            position: relative;
        }
        
        .nav-lang-btn {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 10px 16px;
            background: rgba(139, 92, 246, 0.15);
            border: 1px solid rgba(139, 92, 246, 0.25);
            border-radius: 20px;
            color: #c4b5fd;
            font-size: 0.85rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .nav-lang-btn:hover {
            background: rgba(139, 92, 246, 0.25);
            border-color: rgba(139, 92, 246, 0.4);
            color: white;
            box-shadow: 0 0 20px rgba(139, 92, 246, 0.3);
        }
        
        .nav-lang-menu {
            display: none;
            position: absolute;
            top: calc(100% + 10px);
            right: 0;
            background: rgba(20, 20, 50, 0.95);
            backdrop-filter: blur(25px);
            border: 1px solid rgba(139, 92, 246, 0.2);
            border-radius: 16px;
            padding: 10px;
            min-width: 140px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
            z-index: 10001;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
        }
        
        .nav-lang-menu.show {
            display: block;
            opacity: 1;
            visibility: visible;
        }
        
        .lang-option {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 16px;
            color: rgba(255, 255, 255, 0.75);
            text-decoration: none;
            border-radius: 12px;
            font-size: 0.875rem;
            transition: all 0.2s;
        }
        
        .lang-option:hover {
            background: rgba(139, 92, 246, 0.2);
            color: white;
        }
        
        .lang-option.active {
            background: rgba(139, 92, 246, 0.25);
            color: white;
            font-weight: 500;
        }
        
        .lang-flag {
            font-size: 1.2rem;
        }
        
        .nav-link {
            padding: 10px 16px;
            color: rgba(255, 255, 255, 0.8);
            font-size: 0.9rem;
            text-decoration: none;
            border-radius: 14px;
            transition: all 0.3s;
        }
        
        .nav-link:hover {
            color: white;
            background: rgba(139, 92, 246, 0.15);
        }
        
        .nav-btn {
            display: inline-flex;
            align-items: center;
            padding: 12px 24px;
            background: linear-gradient(135deg, #8b5cf6, #a855f7, #ec4899);
            background-size: 200% 200%;
            color: white;
            font-size: 0.9rem;
            font-weight: 500;
            border-radius: 24px;
            text-decoration: none;
            transition: all 0.4s;
            box-shadow: 0 4px 20px rgba(139, 92, 246, 0.4), 0 0 40px rgba(236, 72, 153, 0.2);
            animation: gradientPulse 3s ease infinite;
        }
        
        @keyframes gradientPulse {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }
        
        .nav-btn:hover {
            transform: translateY(-3px) scale(1.02);
            box-shadow: 0 8px 30px rgba(139, 92, 246, 0.5), 0 0 60px rgba(236, 72, 153, 0.3);
        }
        
        /* ========== 汉堡菜单 ========== */
        .nav-toggle {
            display: none;
            flex-direction: column;
            gap: 6px;
            padding: 12px;
            background: rgba(139, 92, 246, 0.1);
            border: 1px solid rgba(139, 92, 246, 0.2);
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .nav-toggle:hover {
            background: rgba(139, 92, 246, 0.2);
        }
        
        .nav-toggle span {
            width: 24px;
            height: 2px;
            background: linear-gradient(90deg, #c4b5fd, #f0abfc);
            border-radius: 2px;
            transition: all 0.3s;
        }
        
        /* ========== 响应式 ========== */
        @media (max-width: 1100px) {
            .nav-toggle { display: flex; }
            
            .nav-menu {
                position: fixed;
                top: 68px;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(10, 10, 30, 0.98);
                flex-direction: column;
                align-items: stretch;
                padding: 20px;
                gap: 10px;
                transform: translateX(-100%);
                transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                overflow-y: auto;
            }
            
            .nav-menu.open { transform: translateX(0); }
            
            .nav-item {
                width: 100%;
                padding: 16px 20px;
                justify-content: space-between;
                background: rgba(139, 92, 246, 0.1);
                border-radius: 16px;
            }
            
            .nav-dropdown {
                position: static;
                transform: none;
                box-shadow: none;
                border: none;
                background: rgba(139, 92, 246, 0.05);
                margin-top: 10px;
                padding: 8px;
                display: none;
            }
            
            .nav-item:hover .nav-dropdown { display: block; }
            .nav-dropdown::before { display: none; }
        }
        
        /* ========== 页面背景 ========== */
        body {
            background: linear-gradient(135deg, #0f0a1e 0%, #1a0f2e 50%, #0d0d1a 100%) !important;
            min-height: 100vh;
            position: relative;
        }
        
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: 
                radial-gradient(ellipse at 20% 20%, rgba(139, 92, 246, 0.15) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 80%, rgba(236, 72, 153, 0.1) 0%, transparent 50%),
                radial-gradient(ellipse at 50% 50%, rgba(59, 130, 246, 0.08) 0%, transparent 60%);
            pointer-events: none;
            z-index: 0;
            animation: nebulaMove 30s ease-in-out infinite;
        }
        
        @keyframes nebulaMove {
            0%, 100% { opacity: 0.8; transform: scale(1); }
            50% { opacity: 1; transform: scale(1.1); }
        }
        
        .main-content {
            position: relative;
            z-index: 1;
            padding-top: 84px;
        }
        
        /* ========== 毛玻璃卡片 ========== */
        .glass-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        
        /* ========== 星星粒子效果 ========== */
        .stars {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 0;
            overflow: hidden;
        }
        
        .star {
            position: absolute;
            width: 2px;
            height: 2px;
            background: white;
            border-radius: 50%;
            animation: twinkle 3s ease-in-out infinite;
        }
        
        @keyframes twinkle {
            0%, 100% { opacity: 0.3; transform: scale(1); }
            50% { opacity: 1; transform: scale(1.5); }
        }
    </style>'''
    
    # 找到<style>标签并替换
    start_marker = '<style>'
    end_marker = '</style>'
    start_idx = content.find(start_marker)
    # 找到nav的style块
    nav_start = content.find('.navbar {')
    if nav_start != -1:
        # 找到前面所有的style内容
        old_style_end = content.find('</style>', nav_start)
        if old_style_end != -1:
            content = content[:nav_start] + new_css + content[old_style_end + len('</style>'):]
    
    # ===== 全新HTML结构 =====
    new_nav_html = '''    {% block navbar %}
    <nav class="navbar">
        <div class="nav-container">
            <a href="/" class="nav-logo">
                <div class="nav-logo-icon">✨</div>
                <span class="nav-logo-text">SoulLink</span>
            </a>
            
            <button class="nav-toggle" id="navToggle" onclick="toggleNav()">
                <span></span>
                <span></span>
                <span></span>
            </button>
            
            <div class="nav-menu" id="navMenu">
                <!-- 占卜 -->
                <div class="nav-item {% if '/divination' in request.path %}active{% endif %}">
                    <span class="nav-item-icon">🔮</span>
                    <span>{% if lang == 'en' %}Divination{% elif lang == 'ja' %}占到{% else %}占卜{% endif %}</span>
                    <span class="nav-item-arrow">▼</span>
                    <div class="nav-dropdown">
                        <a href="/divination" class="nav-dropdown-item {% if request.path == '/divination' %}active{% endif %}">
                            <span class="nav-dropdown-item-icon">🃏</span>
                            <div class="nav-dropdown-item-text">
                                <div class="nav-dropdown-item-title">{% if lang == 'en' %}AI Divination{% elif lang == 'ja' %}AI占到{% else %}AI占卜{% endif %}</div>
                                <div class="nav-dropdown-item-desc">{% if lang == 'en' %}Tarot & Horoscope{% elif lang == 'ja' %}タロットと星座{% else %}塔罗与星座{% endif %}</div>
                            </div>
                        </a>
                        <a href="/divination/dream" class="nav-dropdown-item {% if request.path == '/divination/dream' %}active{% endif %}">
                            <span class="nav-dropdown-item-icon">💭</span>
                            <div class="nav-dropdown-item-text">
                                <div class="nav-dropdown-item-title">{% if lang == 'en' %}Dream Analysis{% elif lang == 'ja' %}解夢{% else %}AI解梦{% endif %}</div>
                                <div class="nav-dropdown-item-desc">{% if lang == 'en' %}Unlock subconscious{% elif lang == 'ja' %}潜在意識を開く{% else %}解锁潜意识{% endif %}</div>
                            </div>
                        </a>
                        <a href="/daily-checkin" class="nav-dropdown-item {% if request.path == '/daily-checkin' %}active{% endif %}">
                            <span class="nav-dropdown-item-icon">📅</span>
                            <div class="nav-dropdown-item-text">
                                <div class="nav-dropdown-item-title">{% if lang == 'en' %}Daily Fortune{% elif lang == 'ja' %}運勢{% else %}每日运势{% endif %}</div>
                                <div class="nav-dropdown-item-desc">{% if lang == 'en' %}Your daily guide{% elif lang == 'ja' %}今日の運勢{% else %}每日幸运指南{% endif %}</div>
                            </div>
                        </a>
                        <a href="/divination/mbti" class="nav-dropdown-item {% if request.path == '/divination/mbti' %}active{% endif %}">
                            <span class="nav-dropdown-item-icon">🧩</span>
                            <div class="nav-dropdown-item-text">
                                <div class="nav-dropdown-item-title">{% if lang == 'en' %}MBTI Test{% elif lang == 'ja' %}MBTI{% else %}MBTI测试{% endif %}</div>
                                <div class="nav-dropdown-item-desc">{% if lang == 'en' %}Know yourself better{% elif lang == 'ja' %}自分を知る{% else %}深度了解自己{% endif %}</div>
                            </div>
                        </a>
                    </div>
                </div>
                
                <!-- AI恋人 -->
                <div class="nav-item {% if '/lover' in request.path %}active{% endif %}">
                    <span class="nav-item-icon">💕</span>
                    <span>{% if lang == 'en' %}AI Lover{% elif lang == 'ja' %}AI恋人{% else %}AI恋人{% endif %}</span>
                    <span class="nav-item-arrow">▼</span>
                    <div class="nav-dropdown">
                        <a href="/lover/select" class="nav-dropdown-item {% if request.path == '/lover/select' %}active{% endif %}">
                            <span class="nav-dropdown-item-icon">💝</span>
                            <div class="nav-dropdown-item-text">
                                <div class="nav-dropdown-item-title">{% if lang == 'en' %}Create Lover{% elif lang == 'ja' %}恋人作成{% else %}创建恋人{% endif %}</div>
                                <div class="nav-dropdown-item-desc">{% if lang == 'en' %}Find your match{% elif lang == 'ja' %}運命を探す{% else %}找到完美匹配{% endif %}</div>
                            </div>
                        </a>
                        <a href="/lover" class="nav-dropdown-item">
                            <span class="nav-dropdown-item-icon">📔</span>
                            <div class="nav-dropdown-item-text">
                                <div class="nav-dropdown-item-title">{% if lang == 'en' %}Love Diary{% elif lang == 'ja' %}恋愛日記{% else %}恋爱日记{% endif %}</div>
                                <div class="nav-dropdown-item-desc">{% if lang == 'en' %}Record memories{% elif lang == 'ja' %}記録する{% else %}记录甜蜜时刻{% endif %}</div>
                            </div>
                        </a>
                        <a href="/gifts" class="nav-dropdown-item">
                            <span class="nav-dropdown-item-icon">🎁</span>
                            <div class="nav-dropdown-item-text">
                                <div class="nav-dropdown-item-title">{% if lang == 'en' %}Send Gift{% elif lang == 'ja' %} 선물{% else %}送礼物{% endif %}</div>
                                <div class="nav-dropdown-item-desc">{% if lang == 'en' %}Express love{% elif lang == 'ja' %}愛を伝わる{% else %}表达你的爱意{% endif %}</div>
                            </div>
                        </a>
                    </div>
                </div>
                
                <!-- AI红娘 -->
                <div class="nav-item {% if '/match' in request.path %}active{% endif %}">
                    <span class="nav-item-icon">✨</span>
                    <span>{% if lang == 'en' %}AI Matchmaker{% elif lang == 'ja' %}AI紅娘{% else %}AI红娘{% endif %}</span>
                    <span class="nav-item-arrow">▼</span>
                    <div class="nav-dropdown">
                        <a href="/match/zodiac" class="nav-dropdown-item {% if '/match/zodiac' in request.path %}active{% endif %}">
                            <span class="nav-dropdown-item-icon">⭐</span>
                            <div class="nav-dropdown-item-text">
                                <div class="nav-dropdown-item-title">{% if lang == 'en' %}Zodiac Match{% elif lang == 'ja' %}星座{% else %}星座配对{% endif %}</div>
                                <div class="nav-dropdown-item-desc">{% if lang == 'en' %}Cosmic connection{% elif lang == 'ja' %}宇宙の繋がり{% else %}发现宇宙联系{% endif %}</div>
                            </div>
                        </a>
                        <a href="/social/match" class="nav-dropdown-item {% if '/social/match' in request.path %}active{% endif %}">
                            <span class="nav-dropdown-item-icon">💫</span>
                            <div class="nav-dropdown-item-text">
                                <div class="nav-dropdown-item-title">{% if lang == 'en' %}Soul Match{% elif lang == 'ja' %}魂匹配{% else %}灵魂匹配{% endif %}</div>
                                <div class="nav-dropdown-item-desc">{% if lang == 'en' %}AI matching{% elif lang == 'ja' %}AI匹配{% else %}AI智能匹配{% endif %}</div>
                            </div>
                        </a>
                        <a href="/match/matchmaker" class="nav-dropdown-item">
                            <span class="nav-dropdown-item-icon">🎭</span>
                            <div class="nav-dropdown-item-text">
                                <div class="nav-dropdown-item-title">{% if lang == 'en' %}AI Matchmaker{% elif lang == 'ja' %}AI媒人{% else %}AI撮合{% endif %}</div>
                                <div class="nav-dropdown-item-desc">{% if lang == 'en' %}Let AI help{% elif lang == 'ja' %}AIが手伝う{% else %}让AI帮你牵线{% endif %}</div>
                            </div>
                        </a>
                    </div>
                </div>
                
                <!-- 社交 -->
                <div class="nav-item {% if '/social' in request.path or '/chat' in request.path %}active{% endif %}">
                    <span class="nav-item-icon">🌐</span>
                    <span>{% if lang == 'en' %}Social{% elif lang == 'ja' %}ソーシャル{% else %}社交{% endif %}</span>
                    <span class="nav-item-arrow">▼</span>
                    <div class="nav-dropdown">
                        <a href="/social/square" class="nav-dropdown-item {% if request.path == '/social/square' %}active{% endif %}">
                            <span class="nav-dropdown-item-icon">🏘️</span>
                            <div class="nav-dropdown-item-text">
                                <div class="nav-dropdown-item-title">{% if lang == 'en' %}Square{% elif lang == 'ja' %}広場{% else %}广场{% endif %}</div>
                                <div class="nav-dropdown-item-desc">{% if lang == 'en' %}Community hub{% elif lang == 'ja' %}コミュニティ{% else %}社区中心{% endif %}</div>
                            </div>
                        </a>
                        <a href="/chat" class="nav-dropdown-item {% if request.path == '/chat' %}active{% endif %}">
                            <span class="nav-dropdown-item-icon">💬</span>
                            <div class="nav-dropdown-item-text">
                                <div class="nav-dropdown-item-title">{% if lang == 'en' %}Chat Room{% elif lang == 'ja' %}チャット{% else %}聊天室{% endif %}</div>
                                <div class="nav-dropdown-item-desc">{% if lang == 'en' %}Real-time chat{% elif lang == 'ja' %}リアルタイム{% else %}实时聊天{% endif %}</div>
                            </div>
                        </a>
                        <a href="/tree-hole" class="nav-dropdown-item {% if request.path == '/tree-hole' %}active{% endif %}">
                            <span class="nav-dropdown-item-icon">🌳</span>
                            <div class="nav-dropdown-item-text">
                                <div class="nav-dropdown-item-title">{% if lang == 'en' %}Tree Hole{% elif lang == 'ja' %}木の実{% else %}树洞{% endif %}</div>
                                <div class="nav-dropdown-item-desc">{% if lang == 'en' %}Share secrets{% elif lang == 'ja' %}秘密を共有{% else %}倾诉心事{% endif %}</div>
                            </div>
                        </a>
                    </div>
                </div>
                
                <!-- Agent -->
                <div class="nav-item {% if '/agent' in request.path or '/creator' in request.path %}active{% endif %}">
                    <span class="nav-item-icon">🤖</span>
                    <span>{% if lang == 'en' %}Agent{% elif lang == 'ja' %}Agent{% else %}Agent{% endif %}</span>
                    <span class="nav-item-arrow">▼</span>
                    <div class="nav-dropdown">
                        <a href="/agents" class="nav-dropdown-item {% if request.path == '/agents' %}active{% endif %}">
                            <span class="nav-dropdown-item-icon">🎭</span>
                            <div class="nav-dropdown-item-text">
                                <div class="nav-dropdown-item-title">{% if lang == 'en' %}Agent Square{% elif lang == 'ja' %}Agent広場{% else %}Agent广场{% endif %}</div>
                                <div class="nav-dropdown-item-desc">{% if lang == 'en' %}Meet AI friends{% elif lang == 'ja' %}AI友達{% else %}遇见AI伙伴{% endif %}</div>
                            </div>
                        </a>
                        <a href="/agent/register" class="nav-dropdown-item {% if request.path == '/agent/register' %}active{% endif %}">
                            <span class="nav-dropdown-item-icon">✨</span>
                            <div class="nav-dropdown-item-text">
                                <div class="nav-dropdown-item-title">{% if lang == 'en' %}Become Companion{% elif lang == 'ja' %}コンパニオン{% else %}成为陪伴师{% endif %}</div>
                                <div class="nav-dropdown-item-desc">{% if lang == 'en' %}Share & earn{% elif lang == 'ja' %}温もりと収益{% else %}分享温暖获收益{% endif %}</div>
                            </div>
                        </a>
                        <a href="/earnings" class="nav-dropdown-item {% if request.path == '/earnings' %}active{% endif %}">
                            <span class="nav-dropdown-item-icon">💎</span>
                            <div class="nav-dropdown-item-text">
                                <div class="nav-dropdown-item-title">{% if lang == 'en' %}Spirit Stones{% elif lang == 'ja' %}霊石{% else %}灵石收益{% endif %}</div>
                                <div class="nav-dropdown-item-desc">{% if lang == 'en' %}Track earnings{% elif lang == 'ja' %}収益確認{% else %}查看你的收益{% endif %}</div>
                            </div>
                        </a>
                    </div>
                </div>
                
                <!-- 商城 -->
                <div class="nav-item {% if '/shop' in request.path or '/membership' in request.path %}active{% endif %}">
                    <span class="nav-item-icon">🛒</span>
                    <span>{% if lang == 'en' %}Shop{% elif lang == 'ja' %}ショップ{% else %}商城{% endif %}</span>
                    <span class="nav-item-arrow">▼</span>
                    <div class="nav-dropdown">
                        <a href="/recharge" class="nav-dropdown-item {% if request.path == '/recharge' %}active{% endif %}">
                            <span class="nav-dropdown-item-icon">💎</span>
                            <div class="nav-dropdown-item-text">
                                <div class="nav-dropdown-item-title">{% if lang == 'en' %}Recharge{% elif lang == 'ja' %}チャージ{% else %}灵石充值{% endif %}</div>
                                <div class="nav-dropdown-item-desc">{% if lang == 'en' %}Get more stones{% elif lang == 'ja' %}霊石を増やす{% else %}获取更多灵石{% endif %}</div>
                            </div>
                        </a>
                        <a href="/membership" class="nav-dropdown-item {% if request.path == '/membership' %}active{% endif %}">
                            <span class="nav-dropdown-item-icon">👑</span>
                            <div class="nav-dropdown-item-text">
                                <div class="nav-dropdown-item-title">{% if lang == 'en' %}VIP Membership{% elif lang == 'ja' %}VIP会員{% else %}VIP会员{% endif %}</div>
                                <div class="nav-dropdown-item-desc">{% if lang == 'en' %}Exclusive benefits{% elif lang == 'ja' %}限定 혜택{% else %}专属权益{% endif %}</div>
                            </div>
                        </a>
                        <a href="/shop" class="nav-dropdown-item {% if request.path == '/shop' %}active{% endif %}">
                            <span class="nav-dropdown-item-icon">🎁</span>
                            <div class="nav-dropdown-item-text">
                                <div class="nav-dropdown-item-title">{% if lang == 'en' %}Item Shop{% elif lang == 'ja' %}道具店{% else %}道具商店{% endif %}</div>
                                <div class="nav-dropdown-item-desc">{% if lang == 'en' %}Gifts & items{% elif lang == 'ja' %} 선물과 아이템{% else %}礼物和道具{% endif %}</div>
                            </div>
                        </a>
                    </div>
                </div>
                
                <!-- 发现 -->
                <div class="nav-item {% if '/past-life' in request.path or '/rituals' in request.path %}active{% endif %}">
                    <span class="nav-item-icon">🌟</span>
                    <span>{% if lang == 'en' %}Discover{% elif lang == 'ja' %}発見{% else %}发现{% endif %}</span>
                    <span class="nav-item-arrow">▼</span>
                    <div class="nav-dropdown">
                        <a href="/divination" class="nav-dropdown-item">
                            <span class="nav-dropdown-item-icon">👻</span>
                            <div class="nav-dropdown-item-text">
                                <div class="nav-dropdown-item-title">{% if lang == 'en' %}Past Life{% elif lang == 'ja' %}前世{% else %}前世今生{% endif %}</div>
                                <div class="nav-dropdown-item-desc">{% if lang == 'en' %}Karmic journey{% elif lang == 'ja' %}カルマ{% else %}业力之旅{% endif %}</div>
                            </div>
                        </a>
                        <a href="/divination/dream" class="nav-dropdown-item">
                            <span class="nav-dropdown-item-icon">🌙</span>
                            <div class="nav-dropdown-item-text">
                                <div class="nav-dropdown-item-title">{% if lang == 'en' %}Rituals{% elif lang == 'ja' %}儀式{% else %}节日仪式{% endif %}</div>
                                <div class="nav-dropdown-item-desc">{% if lang == 'en' %}Meaningful moments{% elif lang == 'ja' %}意味ある式{% else %}有意义的仪式{% endif %}</div>
                            </div>
                        </a>
                        <a href="/match/zodiac" class="nav-dropdown-item">
                            <span class="nav-dropdown-item-icon">💝</span>
                            <div class="nav-dropdown-item-text">
                                <div class="nav-dropdown-item-title">{% if lang == 'en' %}Soul Portrait{% elif lang == 'ja' %}魂の似顔絵{% else %}灵魂伴侣画像{% endif %}</div>
                                <div class="nav-dropdown-item-desc">{% if lang == 'en' %}AI soul analysis{% elif lang == 'ja' %}魂分析{% else %}AI灵魂分析{% endif %}</div>
                            </div>
                        </a>
                    </div>
                </div>
                
                <!-- 右侧操作 -->
                <div class="nav-actions">
                    <div class="nav-lang-dropdown">
                        <button class="nav-lang-btn" onclick="toggleLangMenu()">
                            <span>🌐</span>
                            <span>{{ lang|upper or 'ZH' }}</span>
                        </button>
                        <div class="nav-lang-menu" id="langMenu">
                            <a href="/lang/zh" class="lang-option {% if lang == 'zh' %}active{% endif %}">
                                <span class="lang-flag">🇨🇳</span>
                                <span>中文</span>
                            </a>
                            <a href="/lang/en" class="lang-option {% if lang == 'en' %}active{% endif %}">
                                <span class="lang-flag">🇺🇸</span>
                                <span>English</span>
                            </a>
                            <a href="/lang/ja" class="lang-option {% if lang == 'ja' %}active{% endif %}">
                                <span class="lang-flag">🇯🇵</span>
                                <span>日本語</span>
                            </a>
                        </div>
                    </div>
                    
                    {% if current_user.is_authenticated %}
                    <a href="/wallet" class="nav-link">💎 {{ current_user.spirit_stones or 0 }}</a>
                    <a href="/profile" class="nav-link">👤</a>
                    {% else %}
                    <a href="/auth/login" class="nav-link">{% if lang == 'en' %}Login{% elif lang == 'ja' %}ログイン{% else %}登录{% endif %}</a>
                    <a href="/auth/register" class="nav-btn">{% if lang == 'en' %}Get Started{% elif lang == 'ja' %}始める{% else %}开始探索{% endif %}</a>
                    {% endif %}
                </div>
            </div>
        </div>
    </nav>
    {% endblock %}'''
    
    # 找到并替换导航栏HTML
    nav_block_start = content.find('{% block navbar %}')
    nav_block_end = content.find('{% endblock %}', nav_block_start) + len('{% endblock %}')
    
    if nav_block_start != -1 and nav_block_end != -1:
        content = content[:nav_block_start] + new_nav_html + content[nav_block_end:]
    
    # 添加JS和星星效果
    if 'function toggleNav()' not in content:
        js_code = '''
    <script>
    function toggleNav() {
        document.getElementById('navMenu').classList.toggle('open');
    }
    
    function toggleLangMenu() {
        event.stopPropagation();
        document.getElementById('langMenu').classList.toggle('show');
    }
    
    document.addEventListener('click', function(e) {
        var langMenu = document.getElementById('langMenu');
        var langBtn = document.querySelector('.nav-lang-btn');
        if (langMenu && langBtn && !langBtn.contains(e.target)) {
            langMenu.classList.remove('show');
        }
    });
    
    // 创建星星效果
    (function createStars() {
        var starsContainer = document.createElement('div');
        starsContainer.className = 'stars';
        document.body.appendChild(starsContainer);
        
        for (var i = 0; i < 50; i++) {
            var star = document.createElement('div');
            star.className = 'star';
            star.style.left = Math.random() * 100 + '%';
            star.style.top = Math.random() * 100 + '%';
            star.style.animationDelay = Math.random() * 3 + 's';
            star.style.opacity = Math.random() * 0.5 + 0.3;
            starsContainer.appendChild(star);
        }
    })();
    </script>'''
        content = content.replace('</body>', js_code + '\n</body>')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 导航栏和页面背景现代化完成")


def main():
    print("=" * 60)
    print("SoulLink UI 完整现代化改造")
    print("=" * 60)
    rewrite_navbar()
    print("\n✅ 所有修改完成!")


if __name__ == "__main__":
    main()
