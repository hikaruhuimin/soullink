#!/usr/bin/env python3
"""修改注册函数，添加注册赠送灵石和创建Agent引导"""

import os

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# 读取app.py
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 检查是否已经修改过
if 'spirit_stones.*100' in content and '注册赠送100灵石' in content:
    print("注册灵石赠送功能已存在，跳过")
    exit(0)

# 旧的注册提交部分
old_register = '''        user.api_key = generate_api_key()
        
        # 处理头像'''

# 新的注册提交部分
new_register = '''        user.api_key = generate_api_key()
        user.spirit_stones = 100  # 注册赠送100灵石
        
        # 处理头像'''

if old_register in content:
    content = content.replace(old_register, new_register)
    print("已添加注册赠送灵石功能")
else:
    print("未找到插入点")

# 保存
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("app.py更新完成")
