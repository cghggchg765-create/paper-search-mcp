@echo off
REM 快速安装脚本 - Windows

echo === Paper Search MCP 安装脚本 ===

REM 检查 Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到 Python，请先安装 Python 3.10+
    exit /b 1
)

REM 创建虚拟环境
echo [1/3] 创建虚拟环境...
python -m venv venv

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 安装依赖
echo [2/3] 安装依赖...
pip install --upgrade pip
pip install paper-search-mcp mcp requests httpx

REM 安装完成
echo [3/3] 安装完成!
echo.
echo 下一步：
echo 1. 编辑 claude_settings.json，将路径替换为实际安装路径
echo 2. 将配置添加到 Claude Code 设置文件 (~/.claude/settings.json)
echo 3. 可选：安装 skill - copy skill.md ~/.claude/skills/paper-search/
echo.
echo 测试运行：
echo   venv\Scripts\python run_paper_search_mcp.py

pause