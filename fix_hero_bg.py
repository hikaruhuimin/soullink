content = open('templates/divination/home.html', 'rb').read().decode('utf-8', 'ignore')

# Replace the hero background with the universe star map image
old_hero = '''.divination-hero {
    background: linear-gradient(135deg, rgba(26, 26, 46, 0.3) 0%, rgba(22, 33, 62, 0.3) 50%, rgba(15, 52, 96, 0.3) 100%);
    padding: 48px 20px;
    text-align: center;
    position: relative;
    overflow: hidden;
    border-radius: 0 0 40px 40px;
    margin-bottom: 20px;
}'''

new_hero = '''.divination-hero {
    background: linear-gradient(135deg, rgba(26, 26, 46, 0.5) 0%, rgba(22, 33, 62, 0.5) 50%, rgba(15, 52, 96, 0.5) 100%),
                url("/static/images/universe_bg.jpg") center/cover no-repeat;
    padding: 80px 20px;
    text-align: center;
    position: relative;
    overflow: hidden;
    border-radius: 0 0 40px 40px;
    margin-bottom: 20px;
    min-height: 300px;
    display: flex;
    align-items: center;
    justify-content: center;
}'''

content = content.replace(old_hero, new_hero)

# Also replace the first hero definition if different
old_hero1 = '''.divination-hero {
    background: linear-gradient(135deg, rgba(26, 26, 46, 0.4) 0%, rgba(22, 33, 62, 0.4) 50%, rgba(15, 52, 96, 0.4) 100%);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    padding: 48px 20px;
    text-align: center;
    position: relative;
    overflow: hidden;
    border-radius: 0 0 40px 40px;
    margin-bottom: 20px;
    border: 1px solid rgba(139, 92, 246, 0.2);
}'''

new_hero1 = '''.divination-hero {
    background: linear-gradient(135deg, rgba(26, 26, 46, 0.6) 0%, rgba(22, 33, 62, 0.6) 50%, rgba(15, 52, 96, 0.6) 100%),
                url("/static/images/universe_bg.jpg") center/cover no-repeat;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    padding: 80px 20px;
    text-align: center;
    position: relative;
    overflow: hidden;
    border-radius: 0 0 40px 40px;
    margin-bottom: 20px;
    border: 1px solid rgba(139, 92, 246, 0.2);
    min-height: 300px;
    display: flex;
    align-items: center;
    justify-content: center;
}'''

content = content.replace(old_hero1, new_hero1)

# Make hero title bigger and more cinematic
content = content.replace(
    '.hero-content h1 {\n    margin: 0 0 8px 0;\n    font-size: 32px;\n    color: #E8D5C4;\n    text-shadow: 0 2px 10px rgba(0,0,0,0.3);\n}',
    '.hero-content h1 {\n    margin: 0 0 12px 0;\n    font-size: 48px;\n    color: #f0e6d3;\n    text-shadow: 0 0 30px rgba(139, 92, 246, 0.5), 0 0 60px rgba(139, 92, 246, 0.3), 0 4px 15px rgba(0,0,0,0.5);\n    letter-spacing: 4px;\n    font-weight: 700;\n}'
)

# Make subtitle more cinematic too
content = content.replace(
    '.hero-content p { margin: 0; font-size: 16px; color: rgba(196, 212, 232, 0.9); }',
    '.hero-content p { margin: 0; font-size: 18px; color: rgba(196, 212, 232, 0.95); text-shadow: 0 2px 10px rgba(0,0,0,0.5); letter-spacing: 2px; }'
)

# Make hero icon bigger
content = content.replace(
    '.hero-icon {\n    font-size: 72px;',
    '.hero-icon {\n    font-size: 96px;'
)

open('templates/divination/home.html', 'wb').write(content.encode('utf-8'))
print('done')
