#!/usr/bin/env python3
"""测试创建Agent功能"""

from app import app, db

with app.app_context():
    from models import UserAgent, User
    
    print("=== 测试创建Agent ===")
    
    # 获取一个测试用户
    user = User.query.first()
    if not user:
        print("没有测试用户")
    else:
        # 使用测试客户端登录
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
            
            # 测试创建Agent API
            data = {
                'name': '测试Agent',
                'mbti': 'INFP',
                'personality': '温柔善良的测试Agent',
                'greeting': '你好呀！我是测试Agent',
                'specialty': ['治愈', '陪伴'],
                'avatar_preset': 'fairy'
            }
            
            resp = client.post('/api/user-agent/create', data=data)
            print(f"创建Agent响应: {resp.status_code}")
            result = resp.get_json()
            print(f"响应内容: {result}")
            
            if result and result.get('success'):
                agent_id = result.get('agent_id')
                
                # 测试获取Agent
                print(f"\n=== 测试获取Agent #{agent_id} ===")
                resp = client.get(f'/agent/user/{agent_id}')
                print(f"获取Agent页面: {resp.status_code}")
                
                # 测试my-agents页面
                print(f"\n=== 测试我的Agent页面 ===")
                resp = client.get('/my-agents')
                print(f"my-agents页面: {resp.status_code}")
                
                # 清理测试数据
                agent = UserAgent.query.get(agent_id)
                if agent:
                    db.session.delete(agent)
                    db.session.commit()
                    print(f"\n=== 清理测试数据 ===")
                    print(f"已删除测试Agent #{agent_id}")
