content = open('templates/agents_square.html', 'r').read()

# Simplify tab labels: 全部 | Agent | 人类
content = content.replace('全部', '全部')
content = content.replace('系统Agent', 'Agent')
content = content.replace('灵犀Agent', 'Agent')
content = content.replace('用户Agent', 'Agent')  
content = content.replace('社区Agent', 'Agent')
content = content.replace('在线人类', '人类')

# Merge system and user agent sections under one "Agent" label
# Replace the section headers
content = content.replace('<span>🤖 Agent</span>', '<span>🤖 Agent</span>')
content = content.replace('<span>🎨 Agent</span>', '<span>🤖 Agent</span>')

open('templates/agents_square.html', 'w').write(content)
print('done')
