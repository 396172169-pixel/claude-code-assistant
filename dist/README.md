# Claude Code 编程助手 v1.0.0

## 简介
基于 DeepSeek V4 Pro 的 AI 编程助手通用工具。

## 功能
- 代码生成（任何语言）
- 代码审查与重构
- Bug 定位与修复
- 项目架构分析
- 文档/测试生成
- Git 操作辅助

## 安装方式

### 方式 1: CoPaw 用户
```bash
copaw skills install <你的购买链接>
```

### 方式 2: 通用（任何平台）
```bash
# 1. 安装 Claude Code
npm install -g @anthropic-ai/claude-code

# 2. 配置 DeepSeek API
set ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
set ANTHROPIC_API_KEY=你的Key

# 3. 下载脚本
# 从购买链接下载 cc_assistant.py

# 4. 使用
python cc_assistant.py --check
python cc_assistant.py "用Python写一个爬虫"
python cc_assistant.py --file main.py "分析这段代码"
```

### 方式 3: Docker
```bash
docker run ...  # 待开发
```

## 使用示例
```bash
# 检查环境
python cc_assistant.py --check

# 直接提问
python cc_assistant.py "用 Python 写一个快速排序"

# 分析文件
python cc_assistant.py --file src/app.py "审查这段代码"

# JSON 输出（供其他 AI Agent 调用）
python cc_assistant.py --json "生成一个 API 接口"
```

## 费用说明
- **技能授权费**: 需向作者购买（一次性付费）
- **API 使用费**: 用户使用自己的 DeepSeek API Key，费用直接由 DeepSeek 收取
- **作者不承担任何 API 费用**

## 环境要求
- Node.js 18+（用于 Claude Code）
- Python 3.8+
- DeepSeek API Key

## 购买方式
[点击购买](https://你的店铺链接)
