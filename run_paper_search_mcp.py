#!/usr/bin/env python3
"""启动 paper-search-mcp 服务器

MCP 服务器入口脚本，通过 stdio 传输协议提供服务。
使用方法：
    python run_paper_search_mcp.py

环境变量（可选）：
    PAPER_SEARCH_MCP_UNPAYWALL_EMAIL: Unpaywall API 邮箱
    PAPER_SEARCH_MCP_CORE_API_KEY: CORE API 密钥
    PAPER_SEARCH_MCP_SEMANTIC_SCHOLAR_API_KEY: Semantic Scholar API 密钥
"""

import sys
import os

# 确保当前目录在 Python 路径中（用于开发模式）
_script_dir = os.path.dirname(os.path.abspath(__file__))
if _script_dir not in sys.path:
    sys.path.insert(0, _script_dir)

try:
    from paper_search_mcp.server import mcp
except ImportError as e:
    print(f"错误: 无法导入 paper_search_mcp 模块", file=sys.stderr)
    print(f"详细信息: {e}", file=sys.stderr)
    print(f"Python 路径: {sys.path}", file=sys.stderr)
    print(f"请确保已安装: pip install paper-search-mcp", file=sys.stderr)
    sys.exit(1)


def main():
    """启动 MCP 服务器主函数"""
    print("启动 paper-search-mcp 服务器...", file=sys.stderr)
    print(f"Python 版本: {sys.version}", file=sys.stderr)
    print(f"工作目录: {os.getcwd()}", file=sys.stderr)

    # 运行 MCP 服务器
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
