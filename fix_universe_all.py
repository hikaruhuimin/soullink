import re

universe_3d_css = '''
/* Universe 3D background */
.universe-3d-bg {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(135deg, rgba(10, 10, 30, 0.4), rgba(30, 15, 60, 0.3)),
                url("/static/images/universe_bg.jpg") center/cover no-repeat;
    background-size: 140% auto;
    z-index: -1;
    animation: universe3dDrift 90s ease-in-out infinite;
}

@keyframes universe3dDrift {
    0% { 
        background-position: 0% 40%;
        transform: perspective(1000px) rotateY(0deg) rotateX(3deg) scale(1.15);
    }
    25% { 
        background-position: 25% 25%;
        transform: perspective(1000px) rotateY(2deg) rotateX(0deg) scale(1.25);
    }
    50% { 
        background-position: 60% 55%;
        transform: perspective(1000px) rotateY(-2deg) rotateX(-2deg) scale(1.2);
    }
    75% { 
        background-position: 40% 35%;
        transform: perspective(1000px) rotateY(1deg) rotateX(1deg) scale(1.3);
    }
    100% { 
        background-position: 0% 40%;
        transform: perspective(1000px) rotateY(0deg) rotateX(3deg) scale(1.15);
    }
}

.universe-3d-bg::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: radial-gradient(ellipse at 30% 30%, rgba(139, 92, 246, 0.2) 0%, transparent 60%),
                radial-gradient(ellipse at 70% 70%, rgba(59, 130, 246, 0.15) 0%, transparent 50%);
    animation: nebulaPulse 10s ease-in-out infinite alternate;
}

@keyframes nebulaPulse {
    0% { opacity: 0.4; transform: scale(1); }
    50% { opacity: 0.7; transform: scale(1.05); }
    100% { opacity: 0.4; transform: scale(1); }
}
'''

# ===== 1. Fix index.html (homepage) =====
idx = open('templates/index.html', 'r').read()

if 'universe-3d-bg' not in idx:
    # Add 3D background CSS
    style_end = idx.find('</style>')
    if style_end >= 0:
        idx = idx[:style_end] + universe_3d_css + idx[style_end:]
    
    # Change hero-section to use universe image as background
    idx = idx.replace(
        'background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);',
        'background: linear-gradient(135deg, rgba(26, 26, 46, 0.6) 0%, rgba(22, 33, 62, 0.6) 50%, rgba(15, 52, 96, 0.6) 100%),\n                url("/static/images/universe_bg.jpg") center/cover no-repeat;\n    background-size: 140% auto;\n    animation: universe3dDrift 90s ease-in-out infinite;'
    )
    
    # Add perspective to hero
    idx = idx.replace(
        'overflow: hidden;\n}',
        'overflow: hidden;\n    perspective: 1000px;\n    transform-style: preserve-3d;\n}'
    )
    
    # Make hero text glow
    idx = idx.replace(
        '.hero-title .highlight {',
        '.hero-title .highlight {\n    text-shadow: 0 0 30px rgba(139, 92, 246, 0.5), 0 0 60px rgba(139, 92, 246, 0.3);'
    )
    
    # Add the universe background div
    bg_div = '\n<div class="universe-3d-bg"></div>\n'
    content_block = idx.find('{% block content %}')
    if content_block >= 0:
        insert_pos = content_block + len('{% block content %}')
        idx = idx[:insert_pos] + bg_div + idx[insert_pos:]
    
    open('templates/index.html', 'w').write(idx)
    print('homepage done')
else:
    print('homepage already has bg')

# ===== 2. Fix chat_home.html =====
chat = open('templates/chat_home.html', 'r').read()

if 'universe-3d-bg' not in chat:
    # Add 3D background CSS
    style_end = chat.find('</style>')
    if style_end >= 0:
        chat = chat[:style_end] + universe_3d_css + chat[style_end:]
    
    # Add the universe background div
    bg_div = '\n<div class="universe-3d-bg"></div>\n'
    content_block = chat.find('{% block content %}')
    if content_block >= 0:
        insert_pos = content_block + len('{% block content %}')
        chat = chat[:insert_pos] + bg_div + chat[insert_pos:]
    
    # Make chat cards semi-transparent for dark bg
    card_css = '''
.chat-card, .chat-room-card, .chat-item {
    background: rgba(20, 15, 40, 0.65) !important;
    backdrop-filter: blur(15px) !important;
    -webkit-backdrop-filter: blur(15px) !important;
    border: 1px solid rgba(139, 92, 246, 0.2) !important;
    color: #e2d9f3 !important;
}

.chat-home h1, .chat-home h2, .chat-home h3 {
    color: #e0d0ff !important;
    text-shadow: 0 0 20px rgba(139, 92, 246, 0.3);
}

.chat-home p, .chat-home span, .chat-home label {
    color: rgba(255, 255, 255, 0.85) !important;
}

.chat-home input, .chat-home textarea {
    background: rgba(30, 20, 60, 0.6) !important;
    border: 1px solid rgba(139, 92, 246, 0.3) !important;
    color: #fff !important;
}
'''
    style_end = chat.find('</style>')
    if style_end >= 0:
        chat = chat[:style_end] + card_css + chat[style_end:]
    
    open('templates/chat_home.html', 'w').write(chat)
    print('chat home done')
else:
    print('chat home already has bg')

# ===== 3. Fix chat_dm.html =====
try:
    dm = open('templates/chat_dm.html', 'r').read()
    if 'universe-3d-bg' not in dm:
        style_end = dm.find('</style>')
        if style_end >= 0:
            dm = dm[:style_end] + universe_3d_css + dm[style_end:]
        
        bg_div = '\n<div class="universe-3d-bg"></div>\n'
        content_block = dm.find('{% block content %}')
        if content_block >= 0:
            insert_pos = content_block + len('{% block content %}')
            dm = dm[:insert_pos] + bg_div + dm[insert_pos:]
        
        open('templates/chat_dm.html', 'w').write(dm)
        print('chat dm done')
except Exception as e:
    print(f'chat dm error: {e}')

# ===== 4. Fix chat_room.html =====
try:
    room = open('templates/chat_room.html', 'r').read()
    if 'universe-3d-bg' not in room:
        style_end = room.find('</style>')
        if style_end >= 0:
            room = room[:style_end] + universe_3d_css + room[style_end:]
        
        bg_div = '\n<div class="universe-3d-bg"></div>\n'
        content_block = room.find('{% block content %}')
        if content_block >= 0:
            insert_pos = content_block + len('{% block content %}')
            room = room[:insert_pos] + bg_div + room[insert_pos:]
        
        open('templates/chat_room.html', 'w').write(room)
        print('chat room done')
except Exception as e:
    print(f'chat room error: {e}')
