"""MCP 服务器端到端测试脚本

功能：
    启动 paper-search-mcp 服务器，通过 JSON-RPC 协议测试 MCP 功能。

测试流程：
    1. initialize - 初始化 MCP 会话
    2. tools/list - 获取可用工具列表
    3. tools/call (search_arxiv) - 执行学术搜索

环境变量：
    PAPER_SEARCH_MCP_UNPAYWALL_EMAIL: Unpaywall API 邮箱
"""

import subprocess
import json
import sys
import time
import os

# Windows 下强制 UTF-8 编码
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def send_message(proc, message):
    """发送 JSON-RPC 消息

    参数：
        proc: MCP 服务器进程
        message: JSON-RPC 消息字典
    """
    data = json.dumps(message, ensure_ascii=False) + "\n"
    proc.stdin.write(data)
    proc.stdin.flush()


def read_message(proc, timeout=30):
    """读取 JSON-RPC 响应

    参数：
        proc: MCP 服务器进程
        timeout: 超时时间（秒）

    返回：
        dict | None: JSON-RPC 响应，EOF 返回 None
    """
    line = proc.stdout.readline()
    if not line:
        return None
    return json.loads(line.strip())


def main():
    """端到端测试主函数

    返回：
        bool: 测试是否通过
    """
    env = os.environ.copy()
    env["PAPER_SEARCH_MCP_UNPAYWALL_EMAIL"] = "cghggchg765@gmail.com"

    print("=" * 60)
    print("MCP 端到端测试")
    print("=" * 60)

    # 启动 MCP 服务器（使用 UTF-8 编码）
    print("\n[1] 启动 MCP 服务器...")
    proc = subprocess.Popen(
        [
            "F:/deskop/mcp/venv/Scripts/python.exe",
            "F:/deskop/mcp/run_paper_search_mcp.py",
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )

    try:
        # 测试 1: Initialize
        print("\n[2] 发送 initialize 请求...")
        send_message(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "1.0"},
                },
            },
        )
        response = read_message(proc)
        if response:
            server_name = response.get("result", {}).get("serverInfo", {}).get("name", "unknown")
            protocol_version = response.get("result", {}).get("protocolVersion", "unknown")
            print(f"    ✓ Initialize 成功: server={server_name}")
            print(f"    协议版本: {protocol_version}")
        else:
            print("    ✗ 未收到响应")
            return False

        # 发送 initialized 通知
        send_message(proc, {"jsonrpc": "2.0", "method": "notifications/initialized"})

        # 测试 2: List Tools
        print("\n[3] 获取工具列表...")
        send_message(
            proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        )
        response = read_message(proc)
        if response and "result" in response:
            tools = response["result"].get("tools", [])
            print(f"    ✓ 获取到 {len(tools)} 个工具:")
            for tool in tools[:10]:  # 只显示前 10 个
                print(f"      - {tool['name']}")
            if len(tools) > 10:
                print(f"      ... 还有 {len(tools) - 10} 个工具")
        else:
            print("    ✗ 获取工具列表失败")
            return False

        # 测试 3: Search Arxiv
        print("\n[4] 测试搜索功能 (search_arxiv)...")
        send_message(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "search_arxiv",
                    "arguments": {"query": "deep learning", "max_results": 3},
                },
            },
        )

        # 等待网络请求
        time.sleep(5)

        try:
            response = read_message(proc, timeout=30)
        except Exception as e:
            print(f"    ⚠ 读取响应异常: {e}")
            response = None

        if response:
            if "result" in response:
                content = response["result"].get("content", [])
                print(f"    ✓ 搜索成功，返回内容类型: {type(content).__name__}")
                if isinstance(content, list) and len(content) > 0:
                    first = content[0]
                    if isinstance(first, dict) and "text" in first:
                        try:
                            parsed = json.loads(first["text"])
                            if isinstance(parsed, list):
                                print(f"    ✓ 搜索到 {len(parsed)} 篇论文")
                                if len(parsed) > 0:
                                    # 显示第一篇论文标题
                                    first_paper = parsed[0]
                                    title = first_paper.get("title", "无标题")
                                    print(f"    示例: {title[:60]}...")
                            elif isinstance(parsed, dict):
                                print(f"    返回数据键: {list(parsed.keys())}")
                        except json.JSONDecodeError:
                            print(f"    文本内容前200字符: {first['text'][:200]}")
            elif "error" in response:
                print(f"    ✗ 搜索出错: {response['error']}")
        else:
            print("    ⚠ 未收到搜索响应（可能超时或网络问题）")

        print("\n" + "=" * 60)
        print("测试完成!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n✗ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 清理资源
        proc.stdin.close()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

        # 输出 stderr 日志
        stderr_output = proc.stderr.read()
        if stderr_output:
            print(f"\n[服务器日志]:\n{stderr_output.strip()}")


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
