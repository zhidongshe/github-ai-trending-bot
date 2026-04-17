# 🤖 GitHub AI Trending Bot

每天自动推送 GitHub 上最热门的 AI 项目到飞书。

## ✨ 功能特点

- 🔄 **自动定时**：每天北京时间 08:00 自动执行
- 📊 **智能筛选**：基于 AI/LLM/Agent/MCP/RAG 等关键词筛选
- 📱 **飞书推送**：美观的卡片消息，支持一键跳转
- 🗂️ **报告归档**：自动保存 Markdown 格式的日报
- 🚀 **零服务器**：完全基于 GitHub Actions，无需额外服务器

## 📁 项目结构

```
github-ai-trending-bot/
├── .github/
│   └── workflows/
│       └── daily-bot.yml      # GitHub Actions 配置
├── src/
│   └── bot.py                 # 主程序
├── requirements.txt           # Python 依赖
├── README.md                  # 本文件
└── DEPLOY.md                  # 部署指南
```

## 🚀 快速部署

### 1. Fork 本项目

点击右上角的 "Fork" 按钮，将项目复制到你的 GitHub 账号下。

### 2. 配置飞书机器人

1. 打开飞书，进入你想接收消息的群聊
2. 点击群设置 → 群机器人 → 添加机器人
3. 选择 "自定义机器人"
4. 复制 Webhook 地址（格式：`https://open.feishu.cn/open-apis/bot/v2/hook/xxxx`）

### 3. 配置 GitHub Secrets

在你的 Fork 仓库中：

1. 点击 **Settings** → **Secrets and variables** → **Actions**
2. 点击 **New repository secret**
3. 添加以下 Secrets：

| Secret 名称 | 值 | 说明 |
|:---|:---|:---|
| `FEISHU_WEBHOOK` | 你的飞书 Webhook 地址 | 必填 |
| `GIT_TOKEN` | 自动生成 | 可选，用于提高 API 限额 |

### 4. 激活 GitHub Actions

1. 进入 **Actions** 标签页
2. 点击 "I understand my workflows, go ahead and enable them"
3. 工作流已激活，将在每天 08:00 自动运行

### 5. 手动测试

1. 进入 **Actions** → **GitHub AI Trending Bot**
2. 点击 **Run workflow** → **Run workflow**
3. 等待约 1 分钟，检查飞书是否收到消息

## ⚙️ 配置选项

### 修改推送时间

编辑 `.github/workflows/daily-bot.yml`：

```yaml
schedule:
  # UTC 时间，北京时间 = UTC + 8
  # 当前配置：每天 UTC 00:00 = 北京时间 08:00
  - cron: '0 0 * * *'
```

常用时间：
- `0 22 * * *` → 北京时间 06:00
- `0 1 * * *` → 北京时间 09:00
- `0 23 * * 1-5` → 工作日 07:00

### 修改搜索关键词

编辑 `src/bot.py` 中的 `queries` 列表：

```python
queries = [
    'AI agent LLM',
    'machine learning',
    'deep learning',
    'MCP',           # 添加你的关键词
    'RAG',
    '你的关键词'      # 新增
]
```

### 修改推送数量

编辑 `src/bot.py`：

```python
return unique_repos[:5]  # 改为需要的数量，如 3 或 10
```

## 📊 数据示例

推送的消息格式：

```
🔥 GitHub AI 热门项目 TOP 5 - 2025-04-17

1. forrestchang/andrej-karpathy-skills
   ⭐ 50,309 stars | TypeScript
   💡 基于 Karpathy 经验的 CLAUDE.md 技能文件
   [查看项目]

2. NousResearch/hermes-agent
   ⭐ 93,986 stars | Python
   💡 自进化 AI Agent
   [查看项目]

...
```

## 🔧 本地开发

```bash
# 克隆项目
git clone https://github.com/你的用户名/github-ai-trending-bot.git
cd github-ai-trending-bot

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
export FEISHU_WEBHOOK="https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
export GIT_TOKEN="ghp_xxx"  # 可选

# 运行测试
cd src
python bot.py
```

## 📝 更新日志

### v1.0.0 (2025-04-17)
- ✅ 基础功能：GitHub API 数据获取
- ✅ 飞书机器人推送
- ✅ GitHub Actions 定时任务
- ✅ Markdown 报告生成

## 🤝 贡献

欢迎提交 Issue 和 PR！

## 📄 许可证

MIT License

---

Made with ❤️ by AI
