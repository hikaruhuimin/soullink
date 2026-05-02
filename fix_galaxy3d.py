import re

# ===== 1. Fix divination home page galaxy animation to 3D =====
content = open('templates/divination/home.html', 'rb').read().decode('utf-8', 'ignore')

# Replace galaxyDrift keyframes with proper 3D rotation
old_drift = re.search(r'@keyframes galaxyDrift \{.*?\}', content, re.DOTALL)
if old_drift:
    content = content.replace(old_drift.group(), '''@keyframes galaxyDrift {
    0% { 
        background-position: 0% 50%;
        transform: perspective(1000px) rotateY(0deg) rotateX(5deg) scale(1.2);
    }
    25% { 
        background-position: 30% 30%;
        transform: perspective(1000px) rotateY(3deg) rotateX(0deg) scale(1.3);
    }
    50% { 
        background-position: 70% 60%;
        transform: perspective(1000px) rotateY(-2deg) rotateX(-3deg) scale(1.25);
    }
    75% { 
        background-position: 50% 40%;
        transform: perspective(1000px) rotateY(2deg) rotateX(2deg) scale(1.35);
    }
    100% { 
        background-position: 100% 50%;
        transform: perspective(1000px) rotateY(0deg) rotateX(5deg) scale(1.2);
    }
}''')

old_rotate = re.search(r'@keyframes galaxyRotate \{.*?\}', content, re.DOTALL)
if old_rotate:
    content = content.replace(old_rotate.group(), '''@keyframes galaxyRotate {
    0% { transform: scale(1) rotate(0deg); opacity: 0.9; }
    33% { transform: scale(1.05) rotate(2deg); opacity: 1; }
    66% { transform: scale(0.98) rotate(-1deg); opacity: 0.95; }
    100% { transform: scale(1) rotate(0deg); opacity: 0.9; }
}''')

# Smoother longer animation
content = content.replace(
    'animation: galaxyDrift 60s ease-in-out infinite alternate;',
    'animation: galaxyDrift 80s ease-in-out infinite;'
)

# Add perspective and 3d to hero
content = content.replace(
    'overflow: hidden;\n    border-radius: 0 0 40px 40px;\n    margin-bottom: 20px;\n    background-size: 150% auto;',
    'overflow: hidden;\n    border-radius: 0 0 40px 40px;\n    margin-bottom: 20px;\n    background-size: 150% auto;\n    perspective: 1000px;\n    transform-style: preserve-3d;'
)

# Add glowing depth overlay
if 'galaxyGlow' not in content:
    glow_css = '''
.divination-hero::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: radial-gradient(ellipse at center, rgba(139, 92, 246, 0.15) 0%, transparent 70%);
    animation: galaxyGlow 8s ease-in-out infinite alternate;
    pointer-events: none;
    z-index: 0;
}

@keyframes galaxyGlow {
    0% { opacity: 0.3; transform: scale(1); }
    50% { opacity: 0.6; transform: scale(1.1); }
    100% { opacity: 0.3; transform: scale(1); }
}
'''
    content = content.replace('</style>', glow_css + '</style>', 1)

open('templates/divination/home.html', 'wb').write(content.encode('utf-8'))
print('divination home done')

# ===== 2. Update dream page with universe background + 3D =====
dream_file = 'templates/divination/divination_dream.html'
try:
    dream = open(dream_file, 'rb').read().decode('utf-8', 'ignore')
    
    # Add universe background + 3D animation CSS
    bg_css = '''
<style>
.dream-universe-bg {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(135deg, rgba(10, 10, 30, 0.7), rgba(30, 15, 60, 0.6)),
                url("/static/images/universe_bg.jpg") center/cover no-repeat;
    background-size: 140% auto;
    z-index: -1;
    animation: dreamUniverseDrift 90s ease-in-out infinite;
    perspective: 1000px;
}

@keyframes dreamUniverseDrift {
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

.dream-universe-bg::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: radial-gradient(ellipse at 40% 30%, rgba(139, 92, 246, 0.2) 0%, transparent 60%),
                radial-gradient(ellipse at 70% 70%, rgba(59, 130, 246, 0.15) 0%, transparent 50%);
    animation: dreamNebulaPulse 10s ease-in-out infinite alternate;
}

@keyframes dreamNebulaPulse {
    0% { opacity: 0.4; transform: scale(1); }
    50% { opacity: 0.7; transform: scale(1.05); }
    100% { opacity: 0.4; transform: scale(1); }
}

/* Make content readable on dark bg */
.dream-page-content {
    position: relative;
    z-index: 1;
}

.dream-page-content .card,
.dream-page-content .dream-card,
.dream-page-content .result-card,
.dream-page-content .encyclopedia-card,
.dream-page-content .section-card,
.dream-page-content .form-card {
    background: rgba(20, 15, 40, 0.65) !important;
    backdrop-filter: blur(15px) !important;
    -webkit-backdrop-filter: blur(15px) !important;
    border: 1px solid rgba(139, 92, 246, 0.2) !important;
    color: #e2d9f3 !important;
}

.dream-page-content h1,
.dream-page-content h2,
.dream-page-content h3 {
    color: #e0d0ff !important;
    text-shadow: 0 0 20px rgba(139, 92, 246, 0.3);
}

.dream-page-content p,
.dream-page-content label,
.dream-page-content span {
    color: rgba(255, 255, 255, 0.85) !important;
}

.dream-page-content input,
.dream-page-content textarea {
    background: rgba(30, 20, 60, 0.6) !important;
    border: 1px solid rgba(139, 92, 246, 0.3) !important;
    color: #fff !important;
}

.dream-page-content input::placeholder,
.dream-page-content textarea::placeholder {
    color: rgba(255, 255, 255, 0.4) !important;
}

.dream-page-content .btn-primary {
    background: linear-gradient(135deg, #8B5CF6, #6D28D9) !important;
    border: none !important;
    box-shadow: 0 0 20px rgba(139, 92, 246, 0.3) !important;
}
</style>
'''
    
    # Add the background div right after <body> or at the start of content block
    if 'dream-universe-bg' not in dream:
        # Insert after {% block content %} or after body
        bg_div = '\n<div class="dream-universe-bg"></div>\n<div class="dream-page-content">\n'
        
        # Find content block
        content_block = dream.find('{% block content %}')
        if content_block >= 0:
            insert_pos = content_block + len('{% block content %}')
            dream = dream[:insert_pos] + bg_div + dream[insert_pos:]
        
        # Add closing div before endblock
        endblock = dream.rfind('{% endblock %}')
        if endblock >= 0:
            dream = dream[:endblock] + '\n</div>\n' + dream[endblock:]
        
        # Add CSS before </head> or in extra_css block
        extra_css = dream.find('{% block extra_css %}')
        if extra_css >= 0:
            insert_css = extra_css + len('{% block extra_css %}')
            dream = dream[:insert_css] + bg_css + dream[insert_css:]
        else:
            # Add before </head>
            dream = dream.replace('</head>', bg_css + '</head>', 1)
    
    open(dream_file, 'wb').write(dream.encode('utf-8'))
    print('dream page done')
except Exception as e:
    print(f'dream page error: {e}')
