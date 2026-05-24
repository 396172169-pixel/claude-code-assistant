#!/usr/bin/env python3
"""
Claude Code 编程助手 — 通用版
================================
基于 DeepSeek V4 Pro 的 AI 编程助手。
支持任何 AI Agent 系统调用，不依赖特定平台。

使用方式:
  python cc_assistant.py "你的编程问题"
  python cc_assistant.py --file 代码文件 "分析这段代码"
  python cc_assistant.py --help

环境变量要求:
  ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
  ANTHROPIC_API_KEY=你的DeepSeek Key
"""

import argparse
import os
import subprocess
import sys
import json
from pathlib import Path


VERSION = "1.0.0"
DEFAULT_MODEL = "deepseek-v4-pro"


def _find_claude() -> str:
    """查找 claude.cmd 可执行文件路径"""
    candidates = [
        os.path.expanduser("~\\AppData\\Roaming\\npm\\claude.cmd"),
        os.path.expanduser("~\\AppData\\Roaming\\npm\\claude"),
        "claude.cmd",
        "claude",
    ]
    for cmd in candidates:
        try:
            r = subprocess.run([cmd, "--version"], capture_output=True, timeout=5)
            if r.returncode == 0:
                return cmd
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            continue
    return "claude.cmd"  # fallback


CLAUDE_BIN = _find_claude()


def _build_env() -> dict:
    """构建子进程环境变量"""
    env = os.environ.copy()
    env["ANTHROPIC_BASE_URL"] = env.get("ANTHROPIC_BASE_URL", "https://api.deepseek.com/anthropic")
    return env


def check_environment() -> list[str]:
    """检查环境依赖，返回缺失项列表"""
    missing = []
    
    if not os.environ.get("ANTHROPIC_API_KEY"):
        missing.append("环境变量 ANTHROPIC_API_KEY 未设置")
    if not os.environ.get("ANTHROPIC_BASE_URL"):
        missing.append("环境变量 ANTHROPIC_BASE_URL 未设置（默认: https://api.deepseek.com/anthropic）")
    
    try:
        r = subprocess.run([CLAUDE_BIN, "--version"], capture_output=True, timeout=10)
        out = r.stdout.decode('utf-8', errors='replace').strip() if r.stdout else ""
        if r.returncode != 0:
            missing.append("Claude Code 未安装。请运行: npm install -g @anthropic-ai/claude-code")
    except FileNotFoundError:
        missing.append("Claude Code 未安装。请运行: npm install -g @anthropic-ai/claude-code")
    except subprocess.TimeoutExpired:
        missing.append("Claude Code 检查超时")
    
    return missing


def run_claude_code(prompt: str, model: str = DEFAULT_MODEL, timeout: int = 120) -> str:
    """调用 Claude Code（DeepSeek 后端）处理编程任务"""
    
    env = _build_env()
    
    cmd = [
        CLAUDE_BIN,
        "--model", model,
        "--print", prompt,
    ]
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=False,  # 二进制模式避免 GBK 编码错误
        timeout=timeout,
        env=env,
    )
    
    # 尝试 UTF-8 解码，兜底 GBK
    stdout = result.stdout.decode('utf-8', errors='replace').strip() if result.stdout else ""
    stderr = result.stderr.decode('utf-8', errors='replace').strip() if result.stderr else ""
    
    if result.returncode != 0:
        error_msg = stderr or stdout or "未知错误"
        raise RuntimeError(f"Claude Code 调用失败 (exit={result.returncode}):\n{error_msg[:500]}")
    
    return stdout


def run_with_file_context(prompt: str, file_paths: list[str], model: str = DEFAULT_MODEL) -> str:
    """读取文件内容后，连同问题一起发给 Claude Code"""
    
    context_parts = []
    
    for fp in file_paths:
        path = Path(fp)
        if not path.exists():
            context_parts.append(f"[not found: {fp}]")
            continue
        
        try:
            content = path.read_text(encoding='utf-8')
            ext = path.suffix
            context_parts.append(f"=== 文件: {fp} ({ext}) ===")
            context_parts.append(content)
            context_parts.append("")
        except Exception as e:
            context_parts.append(f"[读取失败: {fp} - {e}]")
    
    context_parts.append("--- 以上是文件内容 ---")
    context_parts.append("")
    context_parts.append(prompt)
    
    full_prompt = "\n".join(context_parts)
    return run_claude_code(full_prompt, model)


def main():
    parser = argparse.ArgumentParser(
        description="Claude Code 编程助手 (DeepSeek V4 Pro)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python cc_assistant.py "用 Python 写一个快速排序"
  python cc_assistant.py --file app.py "分析这段代码的 Bug"
  python cc_assistant.py --file src/*.py "审查项目代码质量"
  python cc_assistant.py --json "生成一个 JSON Schema"
  python cc_assistant.py --check   # 仅检查环境
        """,
    )
    
    parser.add_argument("prompt", nargs="?", help="编程任务描述")
    parser.add_argument("--file", "-f", action="append", dest="files",
                        help="要分析的代码文件（可多次使用）")
    parser.add_argument("--model", "-m", default=DEFAULT_MODEL,
                        help=f"模型名称（默认: {DEFAULT_MODEL}）")
    parser.add_argument("--timeout", "-t", type=int, default=120,
                        help="超时秒数（默认: 120）")
    parser.add_argument("--json", "-j", action="store_true",
                        help="以 JSON 格式输出")
    parser.add_argument("--check", "-c", action="store_true",
                        help="仅检查环境依赖")
    parser.add_argument("--version", "-v", action="store_true",
                        help="显示版本号")
    
    args = parser.parse_args()
    
    if args.version:
        print(f"Claude Code Assistant v{VERSION}")
        sys.exit(0)
    
    if args.check:
        missing = check_environment()
        if missing:
            print("[检查失败] 环境依赖不满足:\n")
            for item in missing:
                print(f"  [缺失] {item}")
            sys.exit(1)
        else:
            print("[检查通过] 环境正常，可以正常使用")
            try:
                cv_r = subprocess.run([CLAUDE_BIN, "--version"], capture_output=True)
                cv = cv_r.stdout.decode('utf-8', errors='replace').strip()
                print(f"   Claude Code: {cv}")
            except Exception:
                pass
            print(f"   模型: {DEFAULT_MODEL}")
            sys.exit(0)
    
    if not args.prompt:
        parser.print_help()
        print("\n[提示] 请提供编程任务描述")
        sys.exit(1)
    
    # 检查环境
    missing = check_environment()
    if missing:
        print("[检查失败] 环境依赖不满足:\n")
        for item in missing:
            print(f"  [缺失] {item}")
        sys.exit(1)
    
    # 执行
    try:
        if args.files:
            result = run_with_file_context(args.prompt, args.files, args.model)
        else:
            result = run_claude_code(args.prompt, args.model, args.timeout)
        
        if args.json:
            try:
                output = json.dumps({"status": "ok", "result": result}, ensure_ascii=False, indent=2)
            except Exception:
                output = result
        else:
            output = result
        
        print(output)
        
    except subprocess.TimeoutExpired:
        print(f"[超时] 超过{args.timeout}秒，任务可能太复杂")
        sys.exit(1)
    except RuntimeError as e:
        print(f"[失败] {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[错误] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
