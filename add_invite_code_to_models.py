"""
为 User 模型添加 invite_code 字段
"""
import sys
sys.path.insert(0, '/tmp/soullink')

# 读取原文件
with open('/tmp/soullink/models.py', 'r') as f:
    content = f.read()

# 检查是否已存在
if 'invite_code' in content:
    print("invite_code 字段已存在")
else:
    # 在 spirit_stones 后添加 invite_code
    old_text = "    # 虚拟货币\n    spirit_stones = db.Column(db.Integer, default=10)"
    new_text = """    # 虚拟货币
    spirit_stones = db.Column(db.Integer, default=10)
    invite_code = db.Column(db.String(10), unique=True)  # 邀请码"""
    
    content = content.replace(old_text, new_text)
    
    with open('/tmp/soullink/models.py', 'w') as f:
        f.write(content)
    
    print("已添加 invite_code 字段到 User 模型")
