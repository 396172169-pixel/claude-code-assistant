#!/usr/bin/env python3
"""
Claude Code 编程助手 — API Server 版
======================================
提供 HTTP API，任何 AI Agent 都可以通过 API 调用。

支持格式:
  - OpenAI Function Calling 格式
  - Anthropic Tool Use 格式
  - 自定义 JSON 格式

启动:
  python cc_assistant_server.py --port 8080

调用示例:
  curl http://localhost:8080/ask -d '{"prompt":"写一个Python爬虫"}'
"""

import argparse
import json
import os
import subprocess
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

VERSION = "1.0.0"
DEFAULT_MODEL = "deepseek-v4-pro"
PORT = 8080

# 查找 claude 路径
CLAUDE_BIN = None
for c in [
    os.path.expanduser("~\\AppData\\Roaming\\npm\\claude.cmd"),
    "claude.cmd",
    "claude",
]:
    try:
        r = subprocess.run([c, "--version"], capture_output=True, timeout=5)
        if r.returncode == 0:
            CLAUDE_BIN = c
            break
    except Exception:
        continue
if not CLAUDE_BIN:
    CLAUDE_BIN = "claude.cmd"


def call_claude(prompt: str, model: str = DEFAULT_MODEL) -> dict:
    """调用 Claude Code 并返回结构化结果"""
    env = os.environ.copy()
    env["ANTHROPIC_BASE_URL"] = env.get("ANTHROPIC_BASE_URL",
                                         "https://api.deepseek.com/anthropic")
    
    if not env.get("ANTHROPIC_API_KEY"):
        return {"error": "ANTHROPIC_API_KEY 未设置"}
    
    try:
        result = subprocess.run(
            [CLAUDE_BIN, "--model", model, "--print", prompt],
            capture_output=True, timeout=120,
            env=env,
        )
        stdout = result.stdout.decode('utf-8', errors='replace').strip()
        stderr = result.stderr.decode('utf-8', errors='replace').strip()
        
        if result.returncode != 0:
            return {"error": f"调用失败 (exit={result.returncode})", "detail": stderr or stdout[:500]}
        
        return {"result": stdout}
    except subprocess.TimeoutExpired:
        return {"error": "执行超时（>120秒）"}
    except Exception as e:
        return {"error": str(e)}


class SkillHandler(BaseHTTPRequestHandler):
    """HTTP API 处理器"""
    
    def _send_json(self, data: dict, status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def do_GET(self):
        path = urlparse(self.path).path
        
        if path == "/" or path == "/help":
            self._send_json({
                "name": "Claude Code 编程助手",
                "version": VERSION,
                "model": DEFAULT_MODEL,
                "endpoints": {
                    "POST /ask": "提问 {prompt: '你的问题'}",
                    "POST /chat": "OpenAI 兼容格式",
                    "GET /status": "服务状态",
                    "GET /openapi.json": "OpenAPI 规范（用于 GPTs Action）"
                }
            })
        elif path == "/status":
            has_key = bool(os.environ.get("ANTHROPIC_API_KEY"))
            try:
                cv = subprocess.run([CLAUDE_BIN, "--version"], capture_output=True, timeout=5)
                claude_ver = cv.stdout.decode('utf-8', errors='replace').strip()
            except Exception:
                claude_ver = "未安装"
            
            self._send_json({
                "status": "running",
                "version": VERSION,
                "claude_code": claude_ver,
                "api_key_configured": has_key
            })
        elif path == "/openapi.json":
            # OpenAI GPTs Action 兼容格式
            self._send_json({
                "openapi": "3.1.0",
                "info": {"title": "Claude Code 编程助手", "version": VERSION},
                "servers": [{"url": f"http://localhost:{PORT}"}],
                "paths": {
                    "/ask": {
                        "post": {
                            "summary": "编程助手",
                            "operationId": "askProgrammingAssistant",
                            "requestBody": {
                                "required": True,
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "prompt": {"type": "string", "description": "编程任务描述"},
                                                "model": {"type": "string", "default": DEFAULT_MODEL}
                                            },
                                            "required": ["prompt"]
                                        }
                                    }
                                }
                            },
                            "responses": {
                                "200": {
                                    "description": "编程结果",
                                    "content": {"application/json": {"schema": {"type": "object"}}}
                                }
                            }
                        }
                    }
                }
            })
        else:
            self._send_json({"error": "Not found"}, 404)
    
    def do_POST(self):
        path = urlparse(self.path).path
        
        # 读取 body
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode('utf-8')
        
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self._send_json({"error": "无效的 JSON"}, 400)
            return
        
        if path == "/ask":
            prompt = data.get("prompt", "")
            model = data.get("model", DEFAULT_MODEL)
            
            if not prompt:
                self._send_json({"error": "prompt 不能为空"}, 400)
                return
            
            result = call_claude(prompt, model)
            self._send_json(result)
        
        elif path == "/chat":
            # OpenAI 兼容格式
            messages = data.get("messages", [])
            if not messages:
                self._send_json({"error": "messages 不能为空"}, 400)
                return
            
            # 提取最后一条用户消息作为 prompt
            user_msgs = [m["content"] for m in messages if m.get("role") == "user"]
            if not user_msgs:
                self._send_json({"error": "没有用户消息"}, 400)
                return
            
            prompt = user_msgs[-1]
            model = data.get("model", DEFAULT_MODEL)
            result = call_claude(prompt, model)
            
            if "error" in result:
                self._send_json({"error": result["error"]}, 500)
            else:
                self._send_json({
                    "choices": [{
                        "message": {"role": "assistant", "content": result["result"]}
                    }]
                })
        else:
            self._send_json({"error": "Not found"}, 404)
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def log_message(self, format, *args):
        sys.stderr.write(f"[API] {args[0]} {args[1]} {args[2]}\n")


def main():
    parser = argparse.ArgumentParser(description="Claude Code 编程助手 API Server")
    parser.add_argument("--port", "-p", type=int, default=PORT, help=f"端口号（默认: {PORT}）")
    parser.add_argument("--host", default="127.0.0.1", help="监听地址（默认: 127.0.0.1）")
    parser.add_argument("--check", action="store_true", help="检查环境")
    args = parser.parse_args()
    
    if args.check:
        errors = []
        if not os.environ.get("ANTHROPIC_API_KEY"):
            errors.append("ANTHROPIC_API_KEY 未设置")
        if not os.environ.get("ANTHROPIC_BASE_URL"):
            errors.append("ANTHROPIC_BASE_URL 未设置")
        try:
            r = subprocess.run([CLAUDE_BIN, "--version"], capture_output=True, timeout=5)
            if r.returncode == 0:
                ver = r.stdout.decode('utf-8', errors='replace').strip()
                print(f"[OK] Claude Code: {ver}")
            else:
                errors.append("Claude Code 未正常工作")
        except Exception:
            errors.append("Claude Code 未安装")
        
        if errors:
            print("[失败]")
            for e in errors:
                print(f"  [缺失] {e}")
            sys.exit(1)
        else:
            print("[通过] 环境正常")
            return
    
    server = HTTPServer((args.host, args.port), SkillHandler)
    print(f"""
==========================================
  Claude Code 编程助手 API Server
==========================================
  API:     http://{args.host}:{args.port}
  状态:    http://{args.host}:{args.port}/status
  接口:    POST /ask  ({"prompt":"你的问题"})
  OpenAI:  POST /chat (兼容格式)
  OpenAPI: GET  /openapi.json (GPTs用)
==========================================
  任何 Agent 都可以通过 HTTP 调用！
  - OpenAI GPTs     ✅ Action 接入
  - 扣子/Dify       ✅ 自定义工具
  - CoPaw           ✅ 直接调用
  - Claude Code     ✅ 直接调用
  - 其他任何 Agent  ✅ HTTP 就行
==========================================
按 Ctrl+C 停止服务
""")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务已停止")
        server.server_close()


if __name__ == "__main__":
    main()
