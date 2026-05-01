# SoulLink 灵犀 - AI占卜平台

> 命运的指引，源于心与心的连接

![SoulLink](https://img.shields.io/badge/SoulLink-v1.0.0-gold?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge)
![Flask](https://img.shields.io/badge/Flask-3.0-green?style=for-the-badge)

## 🌟 项目简介

SoulLink（灵犀）是一个AI驱动的占卜社交平台，为全球用户提供智能化的命理解读服务。

**核心理念**：让每一次占卜都成为一次与内在自我对话的机会

### MVP核心功能
- 🃏 **塔罗牌占卜**：多种牌阵，AI智能解读
- ⭐ **星盘分析**：基于出生信息的个人星盘
- 📜 **八字简批**：东方命理智慧
- 🔮 **每日运势**：12星座每日运势
- 💕 **恋爱占卜**：复合、暗恋、桃花、姻缘

## 🚀 快速开始

### 环境要求
- Python 3.8+
- pip

### 安装步骤

```bash
# 1. 进入项目目录
cd soullink

# 2. 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行应用
python app.py
```

### 访问应用

打开浏览器访问：**http://localhost:5000**

## 📁 项目结构

```
soullink/
├── app.py                 # Flask应用主文件
├── config.py              # 配置文件
├── models.py              # 数据库模型
├── divination_engine.py   # AI占卜引擎
├── requirements.txt       # Python依赖
├── llms.txt              # AI爬虫文档
├── robots.txt            # 搜索引擎配置
├── sitemap.xml           # 站点地图
├── data/                  # 数据库目录
├── static/
│   ├── css/              # 样式文件
│   ├── js/               # JavaScript
│   └── images/           # 图片资源
└── templates/            # HTML模板
```

## 🎨 设计特点

### 视觉风格
- **神秘优雅**：深色系 + 金色/紫色点缀
- **移动优先**：专为移动端优化的响应式设计
- **卡片式布局**：精美的占卜结果可分享卡片
- **微动画**：翻牌、星光闪烁等过渡效果

### 技术亮点
- 纯原生HTML/CSS/JS，无框架依赖
- Flask + SQLite，轻量级架构
- 流式API支持，实时显示解读
- 三语支持（中文/英文/日文）

## 🔧 配置说明

### AI API配置

在运行前可以设置以下环境变量：

```bash
# Coze API
export COZE_API_KEY="your_api_key"
export COZE_BOT_ID="your_bot_id"

# 或 OpenAI API（备用）
export OPENAI_API_KEY="your_openai_key"
```

> 💡 MVP阶段无需配置API，系统会使用模拟数据进行测试

### 数据库

SQLite数据库文件会自动创建在 `data/soullink.db`

## 📱 页面说明

| 页面 | 路由 | 说明 |
|------|------|------|
| 首页 | `/` | 平台介绍、运势预览入口 |
| 占卜大厅 | `/divination` | 占卜类型选择 |
| 塔罗占卜 | `/divination/tarot` | 塔罗牌互动流程 |
| 每日运势 | `/divination/fortune` | 12星座运势 |
| 恋爱占卜 | `/divination/love` | 情感专项解读 |
| 个人资料 | `/profile` | 用户信息管理 |
| 占卜历史 | `/history` | 历史记录查看 |

## 🔐 用户系统

### 注册/登录
- 邮箱注册
- 密码加密存储
- Session管理

### 权限控制
- 每日3次免费占卜
- VIP会员无限次数
- 占卜记录仅自己可见

## 🌐 国际化

支持三种语言，通过URL参数切换：
- `?lang=zh` - 中文
- `?lang=en` - English
- `?lang=ja` - 日本語

## 🔍 SEO优化

- `/llms.txt` - AI爬虫友好的站点描述
- `/robots.txt` - 搜索引擎访问配置
- `/sitemap.xml` - 站点结构地图
- Schema.org 结构化数据

## 🚢 部署

### 生产环境部署

```bash
# 使用 gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker部署

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

## 📝 开发说明

### 占卜Prompt设计原则
1. 语言温暖有同理心
2. 解读具体不笼统
3. 适当加入神秘元素
4. 支持仪式感描述
5. 给出积极正面的引导

### API预留点
- `divination_engine.py` 中的 `call_ai_api()` 方法
- 支持Coze API和OpenAI API
- 可轻松扩展其他LLM提供商

## 📄 许可证

MIT License

## 👤 作者

SoulLink Team

---

**Made with ✨ and mysterious energy**
