# SoulLink 姻缘匹配功能安装指南

## 功能概述

本次更新为 SoulLink 添加了三个P0优先级功能：

### 1. 星座配对 (`/match/zodiac`)
- 用户选择两个星座，查看配对分析
- 包含144对星座的完整配对数据
- 综合匹配度、爱情匹配、事业匹配
- 性格分析和相处建议
- 支持中文、英文、日语

### 2. AI红娘 (`/match/matchmaker`)
- 基于MBTI、星座、兴趣的智能匹配
- 匿名心动机制（互相心动才配对）
- 每日3次免费心动
- 配对成功后可聊天

### 3. 个人资料卡 (`/match/profile/edit`)
- 头像上传
- 性别、生日（自动算星座）
- MBTI、兴趣标签
- 期待的TA描述

## 安装步骤

### 1. 数据库迁移

运行数据库更新脚本：

```bash
cd soullink
python match_db_update.py
```

或使用Python交互式：

```python
from app import app, db
from match_db_update import upgrade_database

with app.app_context():
    upgrade_database()
```

### 2. 注册路由

在 `app.py` 的 `create_app()` 函数中，找到以下位置：

```python
# Register supplementary routes and lingstone routes
try:
    from routes_supplementary import register_supplementary_routes, register_lingstone_routes, register_agent_api_routes
    register_supplementary_routes(app)
    register_lingstone_routes(app, db)
    register_agent_api_routes(app, db)
except Exception as e:
    import traceback
    print(f"Warning: Could not register routes: {e}")
    traceback.print_exc()
```

在其后添加：

```python
# Register match routes (姻缘匹配)
try:
    from match_routes import register_match_routes
    register_match_routes(app, db)
except Exception as e:
    import traceback
    print(f"Warning: Could not register match routes: {e}")
    traceback.print_exc()
```

### 3. 重启应用

```bash
python start_match.py
```

或直接运行：

```bash
python app.py
```

## 访问地址

- 星座配对：http://localhost:5000/match/zodiac
- AI红娘：http://localhost:5000/match/matchmaker
- 编辑资料：http://localhost:5000/match/profile/edit
- 查看资料：http://localhost:5000/match/profile/{username}

## 文件结构

```
soullink/
├── match_routes.py          # 路由和业务逻辑
├── match_db_update.py       # 数据库更新脚本
├── match_translations.py    # 翻译文件
├── start_match.py           # 启动脚本
├── register_match.py        # 路由注册辅助
├── match_patch.py           # 补丁说明
└── templates/match/
    ├── zodiac_match.html    # 星座配对页面
    ├── matchmaker.html      # AI红娘页面
    ├── profile_edit.html    # 资料编辑页面
    └── profile_view.html    # 资料查看页面
```

## 数据库变更

### users 表新增字段
- `zodiac_sign` - 星座
- `mbti` - MBTI类型
- `interests` - 兴趣标签（逗号分隔）
- `looking_for` - 期待的TA

### 新增表
- `likes` - 心动记录表
- `matches` - 配对记录表

## 注意事项

1. 确保数据库已正确迁移
2. 用户需要完善资料才能使用AI红娘功能
3. 匿名心动机制保护用户隐私
4. 每日免费心动次数限制可通过会员系统扩展

## 技术细节

- 星座配对算法基于传统星座学说
- MBTI匹配包含互补和相似关系
- 兴趣匹配使用Jaccard相似度
- 综合得分 = 星座30% + MBTI40% + 兴趣30%
