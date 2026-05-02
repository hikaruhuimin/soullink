content = open('templates/agents_square.html', 'r').read()

# Remove the user-agents tab button (duplicate Agent tab)
old_tab = '<button class="tab-btn" data-tab="user-agents">'
idx = content.find(old_tab)
if idx >= 0:
    # find the closing </button>
    end_idx = content.find('</button>', idx) + len('</button>')
    content = content[:idx] + content[end_idx:]

# Update agents tab count to include both
content = content.replace(
    '{{ system_agents|length }}\n        </button>',
    '{{ system_agents|length + user_agents|length }}\n        </button>'
)

open('templates/agents_square.html', 'w').write(content)
print('done')
