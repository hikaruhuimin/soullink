#!/usr/bin/env python3
"""Routes patch to add AI chat routes"""
import os
import sys

script_dir = "/tmp/soullink"
routes_path = os.path.join(script_dir, "routes_supplementary.py")

ai_code = '''

# ============ AI智能聊天路由 ============

def register_ai_chat_routes(app, db_session=None):
    from functools import wraps
    from flask import session
    from models import UserAgent, User, AgentChat

    @app.route("/api/agent/<int:agent_id>/chat", methods=["POST"])
    def agent_ai_chat(agent_id):
        try:
            agent = UserAgent.query.get(agent_id)
            if not agent or not agent.is_active:
                return jsonify({"success": False, "error": "Agent不存在或已禁用"}), 404
            
            data = request.get_json() or {}
            user_message = data.get("message", "").strip()
            chat_history = data.get("chat_history", [])
            
            if not user_message:
                return jsonify({"success": False, "error": "消息不能为空"}), 400
            
            agent.chat_count = (agent.chat_count or 0) + 1
            
            ai_reply, is_ai = generate_ai_reply(
                agent=agent,
                user_message=user_message,
                chat_history=chat_history,
                temperature=0.8,
                max_tokens=300
            )
            
            try:
                current_user_id = session.get("user_id")
                chat_record = AgentChat(
                    agent_id=agent.id,
                    user_id=current_user_id or 0,
                    user_message=user_message,
                    agent_response=ai_reply,
                    is_ai_generated=is_ai
                )
                db.session.add(chat_record)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
            
            return jsonify({
                "success": True,
                "message": ai_reply,
                "is_ai": is_ai,
                "agent_name": agent.name,
                "chat_count": agent.chat_count
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/agent/<int:agent_id>/history", methods=["GET"])
    def agent_chat_history(agent_id):
        try:
            agent = UserAgent.query.get(agent_id)
            if not agent:
                return jsonify({"success": False, "error": "Agent不存在"}), 404
            
            page = request.args.get("page", 1, type=int)
            per_page = request.args.get("per_page", 20, type=int)
            
            history_query = AgentChat.query.filter_by(agent_id=agent_id) \\
                .order_by(AgentChat.created_at.desc()) \\
                .paginate(page=page, per_page=per_page, error_out=False)
            
            return jsonify({
                "success": True,
                "history": [{"id": c.id, "user_message": c.user_message, "agent_response": c.agent_response, "created_at": c.created_at.isoformat() if c.created_at else None} for c in history_query.items],
                "total": history_query.total,
                "page": page,
                "per_page": per_page
            })
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/agent/<int:agent_id>/config", methods=["GET"])
    def agent_config_check(agent_id):
        try:
            agent = UserAgent.query.get(agent_id)
            if not agent:
                return jsonify({"success": False, "error": "Agent不存在"}), 404
            
            provider = get_llm_provider()
            ai_enabled = bool(provider)
            llm = "none"
            if os.environ.get("DEEPSEEK_API_KEY"): llm = "deepseek"
            elif os.environ.get("OPENAI_API_KEY"): llm = "openai"
            
            return jsonify({
                "success": True,
                "ai_enabled": ai_enabled,
                "llm_provider": llm,
                "agent_info": {"id": agent.id, "name": agent.name, "personality": agent.personality, "chat_count": agent.chat_count}
            })
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/agent/<int:agent_id>/stream", methods=["POST"])
    def agent_stream_chat(agent_id):
        from flask import Response
        
        try:
            agent = UserAgent.query.get(agent_id)
            if not agent or not agent.is_active:
                return jsonify({"success": False, "error": "Agent不存在或已禁用"}), 404
            
            data = request.get_json() or {}
            user_message = data.get("message", "").strip()
            chat_history = data.get("chat_history", [])
            
            def generate():
                yield f"data: {{'type': 'start', 'agent_name': '{agent.name}'}}\\n\\n"
                from ai_responder import generate_streaming_reply
                full_reply = ""
                try:
                    for chunk in generate_streaming_reply(agent=agent, user_message=user_message, chat_history=chat_history):
                        full_reply += chunk
                        yield f"data: {{'type': 'chunk', 'content': '{chunk}'}}\\n\\n"
                except Exception as e:
                    yield f"data: {{'type': 'error', 'error': '{str(e)}'}}\\n\\n"
                yield f"data: {{'type': 'end', 'full_reply': '{full_reply}'}}\\n\\n"
            
            return Response(generate(), mimetype="text/event-stream", headers={"Cache-Control": "no-cache"})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/ai/test", methods=["POST"])
    def ai_test():
        data = request.get_json() or {}
        
        class TempAgent:
            def __init__(self, name, personality):
                self.name = name
                self.personality = personality
                self.greeting = f"你好，我是{name}！"
                self.specialty = None
            def get_specialty_list(self):
                return []
        
        temp_agent = TempAgent(data.get("agent_name", "测试助手"), data.get("personality", "温柔善良"))
        reply, is_ai = generate_ai_reply(temp_agent, data.get("message", "你好"))
        
        llm = "none"
        if os.environ.get("DEEPSEEK_API_KEY"): llm = "deepseek"
        elif os.environ.get("OPENAI_API_KEY"): llm = "openai"
        
        return jsonify({"success": True, "reply": reply, "is_ai": is_ai, "provider": llm})

    print("AI智能聊天路由注册成功！")

'''

with open(routes_path, 'r', encoding='utf-8') as f:
    content = f.read()

if 'def register_ai_chat_routes' not in content:
    insert_point = '\ndef register_lingstone_routes(app, db_session=None):'
    if insert_point in content:
        content = content.replace(insert_point, ai_code + insert_point)
    else:
        content = content + ai_code
    
    with open(routes_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('AI chat routes added to routes_supplementary.py')
else:
    print('AI chat routes already exist')
