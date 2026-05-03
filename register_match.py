# 路由注册脚本 - 在app.py中注册姻缘匹配路由
# 运行此脚本后将路由注册到Flask应用

def register_match_routes(app, db):
    """注册姻缘匹配相关路由"""
    import os
    
    # 导入匹配模块
    from match_routes import match_bp, Like, Match, calculate_zodiac, get_zodiac_compatibility, comprehensive_match_score, generate_match_analysis
    from match_routes import ZODIAC_SIGNS, ZODIAC_COMPATIBILITY, MBTI_TYPES, MBTI_COMPLEMENTARY, MBTI_SIMILAR
    from match_routes import calculate_mbti_match, calculate_interest_match
    
    # 注册蓝图
    app.register_blueprint(match_bp)
    
    # 添加上下文处理器注入翻译
    @app.context_processor
    def inject_match_translations():
        from match_translations import MATCH_TRANSLATIONS
        from flask import session
        
        def get_client_lang():
            return session.get('language', 'zh')
        
        def match_translate(key, lang=None):
            if lang is None:
                lang = get_client_lang()
            return MATCH_TRANSLATIONS.get(lang, MATCH_TRANSLATIONS.get('zh', {})).get(key, key)
        
        return dict(match_t=match_translate)
    
    print("✅ 姻缘匹配路由注册成功!")
    return app


def update_models_for_match(db):
    """更新User模型，添加姻缘匹配相关字段"""
    from models import db
    
    # 确保User模型有需要的字段
    # 注意：这些字段需要通过数据库迁移添加
    # 在生产环境中，应该使用 Alembic 进行数据库迁移
    
    # 检查是否需要创建表
    try:
        # 创建 likes 表
        db.create_all()
        print("✅ 数据库表创建成功!")
    except Exception as e:
        print(f"⚠️ 数据库表创建时出现问题: {e}")
    
    return db


def add_match_to_navbar():
    """添加导航栏入口（需要手动修改base.html）"""
    print("""
    ⚠️ 请在 templates/base.html 中添加以下导航入口：
    
    在 nav-menu 中添加：
    <a href="/match/zodiac" class="nav-link" style="color: #ff6b9d;">✨ 星座配对</a>
    <a href="/match/matchmaker" class="nav-link" style="color: #a78bfa;">💘 AI红娘</a>
    
    建议位置：在 "占卜" 链接之后
    """)


def run_integration():
    """运行完整的集成"""
    from app import app, db
    
    print("开始注册姻缘匹配功能...")
    
    # 注册路由
    register_match_routes(app, db)
    
    # 更新模型
    update_models_for_match(db)
    
    # 提示导航栏更新
    add_match_to_navbar()
    
    print("\n✅ 姻缘匹配功能集成完成!")
    print("请重启应用使更改生效。")


if __name__ == '__main__':
    run_integration()
