#!/usr/bin/env python3
"""校园网机构访问 MCP 服务器

功能：
    1. 检测校园网连接状态
    2. 搜索机构订阅的学术数据库
    3. 访问论文页面
    4. 下载论文 PDF

支持数据库：
    IEEE Xplore, ACM DL, SpringerLink, ScienceDirect, Wiley, CNKI, 万方

使用方法：
    python campus_mcp_server.py

环境变量：
    CAMPUS_INSTITUTION: 机构标识符（默认 'neu'）
"""

import sys
import os
import json
import asyncio
from typing import Any, Dict, List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    print("错误: 请安装 mcp 包: pip install mcp", file=sys.stderr)
    sys.exit(1)

from campus_access_tool import (
    CampusAccessTool,
    check_campus_connection,
    search_database,
    access_paper,
    download_pdf,
    DATABASE_CONFIGS,
    INSTITUTION_DOMAINS,
)

server = Server("campus-access-server")
campus_tool = CampusAccessTool()


@server.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="check_campus_connection",
            description="检测校园网连接状态。返回机构信息、可访问数据库列表、图书馆 URL。",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="search_database",
            description="搜索校园网订阅的学术数据库。支持 IEEE、ACM、Springer、ScienceDirect、Wiley、CNKI、万方。",
            inputSchema={
                "type": "object",
                "properties": {
                    "database": {
                        "type": "string",
                        "description": "数据库: ieee, acm, springer, elsevier, wiley, cnki, wanfang",
                        "enum": ["ieee", "acm", "springer", "elsevier", "wiley", "cnki", "wanfang"],
                    },
                    "query": {"type": "string", "description": "搜索关键词"},
                    "max_results": {"type": "integer", "description": "最大结果数，默认 10", "default": 10},
                },
                "required": ["database", "query"],
            },
        ),
        Tool(
            name="access_paper",
            description="访问论文页面，检测是否有 PDF 可下载。校园网环境下自动享受机构订阅权限。",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "论文页面 URL"},
                    "database": {"type": "string", "description": "数据库名称（可选，自动检测）"},
                },
                "required": ["url"],
            },
        ),
        Tool(
            name="download_pdf",
            description="下载论文 PDF。校园网环境下可直接下载机构订阅的论文。",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "论文 URL 或 PDF 直链"},
                    "paper_title": {"type": "string", "description": "论文标题（用于文件名）"},
                },
                "required": ["url"],
            },
        ),
        Tool(
            name="list_databases",
            description="列出支持的数据库和机构。",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    try:
        result = {}

        if name == "check_campus_connection":
            result = check_campus_connection()

        elif name == "search_database":
            result = search_database(
                arguments.get("database", ""),
                arguments.get("query", ""),
                arguments.get("max_results", 10),
            )

        elif name == "access_paper":
            result = access_paper(
                arguments.get("url", ""),
                arguments.get("database"),
            )

        elif name == "download_pdf":
            result = download_pdf(
                arguments.get("url", ""),
                paper_title=arguments.get("paper_title"),
            )

        elif name == "list_databases":
            result = {
                "databases": {k: v["name"] for k, v in DATABASE_CONFIGS.items()},
                "institutions": INSTITUTION_DOMAINS,
                "current_institution": campus_tool.institution,
            }

        else:
            result = {"error": f"未知工具: {name}"}

        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e)}, ensure_ascii=False))]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())