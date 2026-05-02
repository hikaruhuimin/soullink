import re

# Fix dream page
dream = open('templates/divination_dream.html', 'r').read()

bg_css = '''
/* Universe background with 3D rotation */
.dream-universe-bg {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(135deg, rgba(10, 10, 30, 0.5), rgba(30, 15, 60, 0.4)),
                url("/static/images/universe_bg.jpg") center/cover no-repeat;
    background-size: 140% auto;
    z-index: -1;
    animation: dreamUniverseDrift 90s ease-in-out infinite;
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
'''

# Add background div and CSS
if 'dream-universe-bg' not in dream:
    # Add CSS in the style block
    style_end = dream.find('</style>')
    if style_end >= 0:
        dream = dream[:style_end] + bg_css + dream[style_end:]
    
    # Add the background div right after content block
    bg_div = '\n<div class="dream-universe-bg"></div>\n'
    content_block = dream.find('{% block content %}')
    if content_block >= 0:
        insert_pos = content_block + len('{% block content %}')
        dream = dream[:insert_pos] + bg_div + dream[insert_pos:]

open('templates/divination_dream.html', 'w').write(dream)
print('dream page done')

# Fix dream encyclopedia page too
try:
    enc = open('templates/divination_dream_encyclopedia.html', 'r').read()
    if 'dream-universe-bg' not in enc:
        # Add CSS
        style_end = enc.find('</style>')
        if style_end >= 0:
            enc = enc[:style_end] + bg_css + enc[style_end:]
        
        # Add background div
        bg_div = '\n<div class="dream-universe-bg"></div>\n'
        content_block = enc.find('{% block content %}')
        if content_block >= 0:
            insert_pos = content_block + len('{% block content %}')
            enc = enc[:insert_pos] + bg_div + enc[insert_pos:]
        
        open('templates/divination_dream_encyclopedia.html', 'w').write(enc)
        print('encyclopedia page done')
    else:
        print('encyclopedia already has bg')
except Exception as e:
    print(f'encyclopedia error: {e}')
