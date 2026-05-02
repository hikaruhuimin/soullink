content = open('templates/base.html','r').read()

# 1. Remove membership from top nav
content = content.replace(
    '<a href="/membership" class="nav-link">会员</a>\n',
    ''
)
# handle html entity version
content = content.replace(
    '\u003ca href="/membership" class="nav-link"\u003e会员\u003c/a\u003e\n',
    ''
)

# 2. Remove membership from bottom mobile nav
# Find and remove the membership bottom-nav-item block
lines = content.split('\n')
new_lines = []
skip = False
for i, line in enumerate(lines):
    if '/membership' in line and 'bottom-nav-item' in line:
        skip = True
    if skip:
        if '</a>' in line:
            skip = False
            continue
        continue
    new_lines.append(line)
content = '\n'.join(new_lines)

# 3. Update footer links - add membership and contact, ensure they're there
old_footer = '''\u003cdiv class=\"footer-links\"\u003e
                \u003ca href=\"/agents\"\u003eAgent广场\u003c/a\u003e
                \u003ca href=\"/chat\"\u003e聊天室\u003c/a\u003e
                \u003ca href=\"/membership\"\u003e会员中心\u003c/a\u003e
                \u003ca href=\"/recharge\"\u003e充值\u003c/a\u003e
                \u003ca href=\"/faq\"\u003e常见问题\u003c/a\u003e
            \u003c/div\u003e'''

new_footer = '''\u003cdiv class=\"footer-links\"\u003e
                \u003ca href=\"/agents\"\u003eAgent广场\u003c/a\u003e
                \u003ca href=\"/chat\"\u003e聊天室\u003c/a\u003e
                \u003ca href=\"/recharge\"\u003e充值\u003c/a\u003e
                \u003ca href=\"/membership\"\u003e会员中心\u003c/a\u003e
                \u003ca href=\"/contact\"\u003e联系客服\u003c/a\u003e
                \u003ca href=\"/faq\"\u003e常见问题\u003c/a\u003e
            \u003c/div\u003e'''

content = content.replace(old_footer, new_footer)

open('templates/base.html','w').write(content)
print('done')
