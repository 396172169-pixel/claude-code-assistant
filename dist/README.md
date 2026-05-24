# Claude Code 编程助手 v1.0.0

基于 **DeepSeek V4 Pro** 的 AI 编程助手，任何 AI Agent 系统都能接入。

## 📦 三合一交付

```
┌─ CLI 工具 ─────────────────────┐
│  cc_assistant.py               │  任何系统直接运行
├─ API Server ───────────────────┤
│  cc_assistant_server.py        │  任何 Agent HTTP 调用
├─ CoPaw Skill ──────────────────┤
│  SKILL.md + bundle.json        │  CoPaw 原生安装
└────────────────────────────────┘
```

---

## 一、安装方式（任选其一）

### 方式 A：CoPaw 用户
```bash
copaw skills install https://raw.githubusercontent.com/396172169-pixel/claude-code-assistant/master/dist/claude-code-assistant.bundle.json
```

### 方式 B：通用 CLI（任何平台/任何 Agent）
```bash
# 下载
curl -O https://raw.githubusercontent.com/396172169-pixel/claude-code-assistant/master/cc_assistant.py

# 直接使用
python cc_assistant.py "用Python写一个爬虫"
python cc_assistant.py --file main.py "审查这段代码"
python cc_assistant.py --check
```

### 方式 C：API Server（任何 Agent HTTP 调用）
```bash
# 启动服务
python cc_assistant_server.py --port 8080

# 其他 Agent 调用
curl http://localhost:8080/ask -d '{"prompt":"写一个快速排序"}'
```

### 方式 D：Dify / 扣子 / FastGPT 接入
```
工具类型: HTTP API
请求地址: http://localhost:8080/ask
请求方法: POST
请求体:   {"prompt": "{{用户问题}}"}
```

### 方式 E：OpenAI GPTs 接入
```
Action Schema: http://localhost:8080/openapi.json
```

---

## 二、环境要求

```bash
# 1. 安装 Claude Code
npm install -g @anthropic-ai/claude-code

# 2. 配置 DeepSeek API Key（从 platform.deepseek.com 获取）
set ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
set ANTHROPIC_API_KEY=sk-你的Key
```

---

## 三、使用示例

```bash
# 代码生成
python cc_assistant.py "用Python写一个Redis缓存装饰器"

# 代码审查
python cc_assistant.py --file app.py "审查这段代码的安全性问题"

# Bug定位
python cc_assistant.py --file server.log "分析这个日志的错误原因"

# 架构分析
python cc_assistant.py --file src/*.py "分析这个项目的目录结构和架构"

# 测试生成
python cc_assistant.py "为这个函数写单元测试" --file utils.py
```

---

## 四、费用说明

| 费用项 | 谁出 | 说明 |
|--------|:----:|:-----|
| 技能授权费 | **用户 → 作者** | 一次性购买 ¥99 |
| API 调用费 | **用户 → DeepSeek** | DeepSeek 按量计费，约 ¥0.5/百万 token |
| Claude Code | **用户** | 免费开源 |

**作者（你）只收技能授权费，不承担任何 API 费用。**

---

## 五、购买方式

| 方式 | 说明 |
|:----:|:------|
| 💬 微信/支付宝 | 扫码付款 → 自动发送下载链接 |
| 🏪 爱发电 | 搜索「Claude Code 编程助手」|

---

## 六、文件清单

| 文件 | 大小 | 用途 |
|------|:----:|:-----|
| `cc_assistant.py` | 6.5KB | 通用 CLI 工具 |
| `cc_assistant_server.py` | 9.5KB | HTTP API 服务 |
| `dist/claude-code-assistant.bundle.json` | 7.2KB | CoPaw 安装包 |
| `skills/claude-code-assistant/SKILL.md` | 2.1KB | CoPaw 技能文档 |
