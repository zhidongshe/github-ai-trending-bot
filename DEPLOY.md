# 🚀 部署指南

## 步骤 1：Fork 仓库

1. 打开 https://github.com/你的用户名/github-ai-trending-bot
2. 点击右上角的 **Fork** 按钮
3. 等待 Fork 完成

## 步骤 2：获取飞书 Webhook

### 2.1 创建群机器人

1. 在飞书中打开目标群聊
2. 点击右上角 **···** → **设置** → **群机器人**
3. 点击 **添加机器人**
4. 选择 **自定义机器人**
5. 设置机器人名称和描述（如 "GitHub AI Trending"）
6. 点击 **添加**

### 2.2 复制 Webhook 地址

添加成功后，你会看到：

```
Webhook 地址：https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

⚠️ **请务必保存好这个地址，不要泄露给他人**

## 步骤 3：配置 Secrets

### 3.1 进入 Secrets 设置

1. 打开你 Fork 的仓库
2. 点击 **Settings** 标签
3. 左侧菜单选择 **Secrets and variables** → **Actions**
4. 点击 **New repository secret**

### 3.2 添加 FEISHU_WEBHOOK

| 字段 | 值 |
|:---|:---|
| Name | `FEISHU_WEBHOOK` |
| Secret | `https://open.feishu.cn/open-apis/bot/v2/hook/xxx...` |

点击 **Add secret**

### 3.3 添加 GITHUB_TOKEN（可选）

GitHub Token 用于提高 API 访问限额：

1. 打开 https://github.com/settings/tokens
2. 点击 **Generate new token** → **Generate new token (classic)**
3. 设置 Token name: `github-trending-bot`
4. 勾选权限：**public_repo**
5. 点击 **Generate token**
6. 复制生成的 Token

回到 Secrets 设置，添加：

| 字段 | 值 |
|:---|:---|
| Name | `GITHUB_TOKEN` |
| Secret | `ghp_xxxxxxxxxxxx...` |

## 步骤 4：激活 Actions

### 4.1 启用 Actions

1. 点击仓库顶部的 **Actions** 标签
2. 点击 **I understand my workflows, go ahead and enable them**

### 4.2 手动测试运行

1. 点击左侧的 **GitHub AI Trending Bot**
2. 点击右侧的 **Run workflow** → **Run workflow**
3. 等待约 1-2 分钟
4. 查看飞书群是否收到消息

## 步骤 5：验证部署

### 检查清单

- [ ] Fork 完成
- [ ] 飞书机器人已添加
- [ ] Webhook 地址已保存
- [ ] FEISHU_WEBHOOK Secret 已添加
- [ ] GITHUB_TOKEN Secret 已添加（可选）
- [ ] Actions 已启用
- [ ] 手动测试运行成功
- [ ] 飞书收到第一条消息

### 常见问题

#### Q1: 飞书没有收到消息

**排查步骤**：

1. 检查 Actions 日志：
   - 进入 Actions → 点击最新的 workflow run
   - 查看 `Run bot` 步骤的输出

2. 检查 Secret 是否正确：
   - Settings → Secrets → 确认 FEISHU_WEBHOOK 存在

3. 检查飞书机器人：
   - 在飞书群里 @机器人，看是否有响应
   - 确认 Webhook 地址没有过期

#### Q2: GitHub API 限制

**错误信息**：`API rate limit exceeded`

**解决方案**：
- 添加 GITHUB_TOKEN Secret（将限额从 60/小时 提升到 5000/小时）
- 或减少搜索关键词数量

#### Q3: 消息格式错乱

如果飞书消息显示不正常：

1. 检查飞书机器人是否支持卡片消息
2. 或修改 `src/bot.py` 中的 `send_to_feishu` 函数，使用纯文本格式

## 步骤 6：定制配置（可选）

### 修改推送时间

编辑 `.github/workflows/daily-bot.yml`：

```yaml
schedule:
  - cron: '0 1 * * *'  # 北京时间 09:00
```

### 修改搜索关键词

编辑 `src/bot.py`，修改 `queries` 列表：

```python
queries = [
    'AI agent LLM',
    'machine learning',
    '你的关键词',  # 添加
]
```

### 修改推送条数

```python
return unique_repos[:10]  # 推送 10 条
```

## 卸载

如需停止使用：

1. 进入 Settings → Secrets → 删除 FEISHU_WEBHOOK
2. 删除飞书群中的机器人
3. （可选）删除 Fork 的仓库

---

**遇到问题？** 提交 Issue 或联系维护者。
