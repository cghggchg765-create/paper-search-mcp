# Claude Code Skill 安装

将本目录下的 `skill.md` 复制到 Claude Code skills 目录：

## Windows

```powershell
mkdir -p ~/.claude/skills/paper-search
cp skill.md ~/.claude/skills/paper-search/
```

## Linux/macOS

```bash
mkdir -p ~/.claude/skills/paper-search
cp skill.md ~/.claude/skills/paper-search/
```

## 使用

重启 Claude Code 后即可使用 `/paper-search` 命令。

## 注意事项

1. 确保 MCP 服务器已配置（参考 `../claude_settings.json`）
2. 确保虚拟环境已创建并安装依赖
3. 配置中的路径需要替换为实际安装路径
