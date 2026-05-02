content = open('templates/agents_square.html', 'r').read()

# Remove "官方" badge from system agent cards
content = content.replace('<span class="section-badge badge-official">官方</span>', '')
content = content.replace('<span class="section-badge badge-official" style="font-size: 0.625rem; padding: 2px 6px;">官方</span>', '')

# Remove "社区" badge from user agent cards
content = content.replace('<span class="section-badge badge-community">社区</span>', '')
content = content.replace('<span class="section-badge badge-community" style="font-size: 0.625rem; padding: 2px 6px;">社区</span>', '')

# Clean up section labels - simplify
content = content.replace('<span>🤖 系统Agent</span>', '<span>🤖 灵犀Agent</span>')
content = content.replace('<span>🎨 用户Agent</span>', '<span>🎨 社区Agent</span>')

open('templates/agents_square.html', 'w').write(content)
print('done')
