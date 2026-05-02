content = open('templates/base.html', 'r').read()

# 1. Change navbar background to dark cosmic style
old_navbar = '''        .navbar {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: var(--z-sticky);
            background: rgba(253, 252, 250, 0.92);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--color-border-light);
        }'''

new_navbar = '''        .navbar {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: var(--z-sticky);
            background: linear-gradient(135deg, rgba(30, 15, 60, 0.95), rgba(10, 20, 50, 0.95));
            backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(139, 92, 246, 0.3);
            box-shadow: 0 2px 20px rgba(139, 92, 246, 0.15);
        }'''

content = content.replace(old_navbar, new_navbar)

# 2. Make nav height smaller (72px -> 56px)
content = content.replace('height: 72px;', 'height: 56px;')

# 3. Change nav-link colors to light/white for dark bg
old_navlink = '''        .nav-link {
            color: var(--color-text-primary);
            text-decoration: none;
            font-size: 0.9375rem;
            font-weight: 500;
            padding: var(--space-sm) var(--space-md);
            border-radius: var(--radius-full);
            transition: all 0.2s ease;
            position: relative;
        }'''

new_navlink = '''        .nav-link {
            color: rgba(255, 255, 255, 0.85);
            text-decoration: none;
            font-size: 0.875rem;
            font-weight: 500;
            padding: var(--space-sm) var(--space-md);
            border-radius: var(--radius-full);
            transition: all 0.2s ease;
            position: relative;
        }'''

content = content.replace(old_navlink, new_navlink)

# 4. Change nav-link hover
old_hover = '''        .nav-link:hover {
            background: var(--color-bg-warm);
            color: var(--color-accent);
        }'''

new_hover = '''        .nav-link:hover {
            background: rgba(139, 92, 246, 0.2);
            color: #e0d0ff;
        }'''

content = content.replace(old_hover, new_hover)

# 5. Change logo color
content = content.replace('color: var(--color-accent);\n            font-family: var(--font-display);', 
                          'color: #e0d0ff;\n            font-family: var(--font-display);')

# 6. Change nav-lang-btn for dark bg
old_lang = '''        .nav-lang-btn {
            background: var(--color-bg-warm);
            border: 1px solid var(--color-border-light);'''

new_lang = '''        .nav-lang-btn {
            background: rgba(139, 92, 246, 0.15);
            border: 1px solid rgba(139, 92, 246, 0.3);'''

content = content.replace(old_lang, new_lang)

# 7. Fix the 灵石商城 special color for dark bg
content = content.replace('style="color: #11998e; font-weight: 600;"', 'style="color: #7cffc4; font-weight: 600; text-shadow: 0 0 8px rgba(124, 255, 196, 0.4);"')

# 8. Change nav-link active/after color
content = content.replace("background: var(--color-accent);", "background: #8B5CF6;")
content = content.replace("color: var(--color-accent);", "color: #c4b5fd;")

open('templates/base.html', 'w').write(content)
print('done')
