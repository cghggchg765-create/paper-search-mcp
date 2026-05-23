#!/bin/bash
# 快速安装脚本 - Linux/macOS

set -e

echo "=== Paper Search MCP 安装脚本 ==="

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python3，请先安装 Python 3.10+"
    exit 1
fi

# 创建虚拟环境
echo "[1/3] 创建虚拟环境..."
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "[2/3] 安装依赖..."
pip install --upgrade pip
pip install paper-search-mcp mcp requests httpx

# 安装完成
echo "[3/3] 安装完成!"
echo ""
echo "下一步："
echo "1. 编辑 claude_settings.json，将路径替换为实际安装路径"
echo "2. 将配置添加到 Claude Code 设置文件 (~/.claude/settings.json)"
echo "3. 可选：安装 skill - cp skill.md ~/.claude/skills/paper-search/"
echo ""
echo "测试运行："
echo "  venv/bin/python run_paper_search_mcp.py"