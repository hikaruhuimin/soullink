#!/usr/bin/env python3
import app as flask_app

# 查看所有路由
print("好友系统相关路由:")
for rule in flask_app.app.url_map.iter_rules():
    if 'friend' in rule.endpoint or 'dm' in rule.endpoint or 'online' in rule.endpoint:
        print(f'  {rule.endpoint}: {rule.rule}')

print("\n所有路由:")
for rule in flask_app.app.url_map.iter_rules():
    print(f'  {rule.endpoint}: {rule.rule}')
