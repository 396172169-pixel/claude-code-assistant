---
name: claude-code-assistant
description: "调用 Claude Code（DeepSeek V4 Pro 驱动）处理编程任务：代码生成、重构、审查、Bug定位、文档生成、Git操作等。适用于需要深度代码分析或代码生成的场景。触发词：编程、写代码、重构、审查、分析代码、改bug、生成代码、claude"
metadata:
  copaw:
    emoji: "🤖"
    requires:
      - claude（npm包）
      - ANTHROPIC_BASE_URL 和 ANTHROPIC_API_KEY 环境变量
---

# Claude Code 编程助手 Skill

## 概述

利用 **Claude Code CLI**（后端为 **DeepSeek V4 Pro**）处理编程任务。当用户需要深度代码分析、代码生成、重构、代码审查等功能时，使用本 skill。

## 工作原理

```
用户提出编程任务
    ↓
Agent 识别为编程类请求 → 触发本 skill
    ↓
调用 claude --print "任务描述" 
    ↓
Claude Code (DeepSeek V4 Pro) 执行任务
    ↓
返回结果给用户
```

## 何时使用

| 触发场景 | 示例用户提问 |
|----------|-------------|
| 🛠 **代码生成** | "帮我写一个 Python 爬虫" |
| 🔍 **代码分析** | "分析这个项目的架构" |
| 🐛 **Bug 定位** | "这段代码为什么报错" |
| 🔄 **重构优化** | "重构这个函数，提高可读性" |
| 📝 **代码审查** | "审查一下这段代码" |
| 📖 **文档生成** | "给这个模块生成文档" |
| 🧪 **测试生成** | "为这个函数写单元测试" |
| 🔧 **调试** | "这段代码性能瓶颈在哪" |

## 使用方法

### 方式一：简单一问一答

```
ASK: "用 Python 写一个快速排序算法"
```

Agent 将运行：
```bash
claude --model deepseek-v4-pro --print "用 Python 写一个快速排序算法"
```

### 方式二：分析当前项目代码

需要先读取相关文件，然后调用 Claude Code 分析：

```bash
# 读取文件内容后
claude --model deepseek-v4-pro --print "分析以下代码的问题：\n\n[代码内容]"
```

### 方式三：多文件/项目级任务

对于涉及整个项目的任务，直接在项目目录运行：

```bash
cd <项目目录>
claude --model deepseek-v4-pro --print "分析这个项目的整体架构"
```

## 调用步骤

1. **读文件**：如果需要分析现有代码，先用 `read_file` 或 `execute_shell_command` 获取代码内容
2. **构造 Prompt**：把用户问题 + 代码上下文整合成一个清晰的提示词
3. **执行**：用 `execute_shell_command` 执行 `claude --model deepseek-v4-pro --print "提示词"`
4. **整理结果**：把 Claude Code 的返回结果整理后给用户

## 示例 Prompt 模板

### 代码生成
```
请生成一份高质量的 [语言] 代码，实现 [功能描述]。
要求：
- 代码风格规范
- 包含必要的注释
- 处理边界情况
- 附上使用示例
```

### 代码审查
```
请审查以下代码，指出：
1. 潜在的 Bug 和风险
2. 性能优化建议
3. 代码风格问题
4. 安全漏洞

[代码内容]
```

### Bug 定位
```
以下代码运行时出现 [错误信息]，请分析原因并给出修复方案。
上下文：[相关代码]
错误：[错误信息/堆栈]
```

## 注意事项

- **环境变量**：需要 `ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic` 和 `ANTHROPIC_API_KEY`（已在系统环境变量中设置）
- **非交互模式**：使用 `--print` 参数进行非交互式问答
- **长任务**：对于复杂任务，设置合理的 timeout（建议 60-120 秒）
- **代码上下文**：对于需要分析已有代码的场景，先用 `read_file` 读入代码后一并发送
- **不要连带执行**：Claude Code 返回的是分析/代码结果，不要直接执行它返回的代码（除非用户要求）
- **模型选择**：默认使用 `deepseek-v4-pro`，若需要更快响应可改用 `deepseek-v4-flash`
