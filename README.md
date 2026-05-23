# Paper Search MCP

学术论文搜索与校园网机构访问 MCP 服务器。

## 功能特性

### 🔍 学术论文搜索
- **arXiv** - 物理、数学、计算机科学预印本
- **PubMed** - 生物医学文献
- **Google Scholar** - 综合学术搜索
- **bioRxiv/medRxiv** - 生物学和医学预印本

### 🏫 校园网机构访问
- **IEEE Xplore** - 电气电子工程师学会数字图书馆
- **ACM Digital Library** - 计算机协会数字图书馆
- **SpringerLink** - 施普林格学术出版平台
- **ScienceDirect** - 爱思唯尔科学数据库
- **Wiley Online Library** - 威利在线图书馆
- **CNKI** - 中国知网
- **万方数据** - 万方数据知识服务平台

### 📥 论文 PDF 下载
- 自动利用校园网订阅权限下载付费论文
- 支持批量下载
- 自动处理机构认证

### 🛡️ 自动错误修复
- 模块导入错误自动检测与修复
- Windows GBK 编码问题自动处理
- 代理 URL 解析失败自动回退

## 安装

### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/paper-search-mcp.git
cd paper-search-mcp
```

### 2. 创建虚拟环境

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install paper-search-mcp mcp requests httpx
```

## 配置

### Claude Code 配置

将以下配置添加到 Claude Code 的设置文件中（`~/.claude/settings.json` 或项目目录下的 `.claude/settings.json`）：

```json
{
  "mcpServers": {
    "paper-search": {
      "command": "/path/to/paper-search-mcp/venv/Scripts/python.exe",
      "args": ["/path/to/paper-search-mcp/run_paper_search_mcp.py"],
      "env": {
        "PAPER_SEARCH_MCP_UNPAYWALL_EMAIL": "your-email@example.com"
      }
    },
    "campus-access": {
      "command": "/path/to/paper-search-mcp/venv/Scripts/python.exe",
      "args": ["/path/to/paper-search-mcp/campus_mcp_server.py"],
      "env": {
        "CAMPUS_INSTITUTION": "neu"
      }
    }
  }
}
```

### 环境变量说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `PAPER_SEARCH_MCP_UNPAYWALL_EMAIL` | Unpaywall API 邮箱（用于开放获取） | - |
| `CAMPUS_INSTITUTION` | 机构标识符 | `neu` |
| `CAMPUS_PROXY_URL` | 代理服务器地址（可选） | - |

### 支持的机构

共支持 **79 所高校**，所有域名均经过验证。

#### 39所985高校

| 标识符 | 机构 | 标识符 | 机构 |
|--------|------|--------|------|
| `pku` | 北京大学 | `tsinghua` | 清华大学 |
| `fudan` | 复旦大学 | `sjtu` | 上海交通大学 |
| `zju` | 浙江大学 | `ustc` | 中国科学技术大学 |
| `nju` | 南京大学 | `hit` | 哈尔滨工业大学 |
| `buaa` | 北京航空航天大学 | `neu` | 东北大学 |
| `tju` | 天津大学 | `nankai` | 南开大学 |
| `dlut` | 大连理工大学 | `jlu` | 吉林大学 |
| `tongji` | 同济大学 | `seu` | 东南大学 |
| `xmu` | 厦门大学 | `sdu` | 山东大学 |
| `ouc` | 中国海洋大学 | `whu` | 武汉大学 |
| `hust` | 华中科技大学 | `csu` | 中南大学 |
| `scut` | 华南理工大学 | `sysu` | 中山大学 |
| `uestc` | 电子科技大学 | `cqu` | 重庆大学 |
| `xjtu` | 西安交通大学 | `nwpu` | 西北工业大学 |
| `nwsuaf` | 西北农林科技大学 | `lzu` | 兰州大学 |
| `bnu` | 北京师范大学 | `ruc` | 中国人民大学 |
| `bit` | 北京理工大学 | `cau` | 中国农业大学 |
| `muc` | 中央民族大学 | `nwu` | 西北大学 |
| `nudt` | 国防科技大学 | `hnu` | 湖南大学 |
| `ccnu` | 华中师范大学 | | |

#### 重点211高校（32所）

| 标识符 | 机构 | 标识符 | 机构 |
|--------|------|--------|------|
| `bjtu` | 北京交通大学 | `bupt` | 北京邮电大学 |
| `cug` | 中国地质大学 | `cumt` | 中国矿业大学 |
| `hhu` | 河海大学 | `njau` | 南京农业大学 |
| `nuaa` | 南京航空航天大学 | `njust` | 南京理工大学 |
| `nuist` | 南京信息工程大学 | `scu` | 四川大学 |
| `swjtu` | 西南交通大学 | `swufe` | 西南财经大学 |
| `szu` | 深圳大学 | `gdut` | 广东工业大学 |
| `ecust` | 华东理工大学 | `shu` | 上海大学 |
| `ecnu` | 华东师范大学 | `suda` | 苏州大学 |
| `whut` | 武汉理工大学 | `hdu` | 杭州电子科技大学 |
| `zstu` | 浙江理工大学 | `cqupt` | 重庆邮电大学 |
| `jiangnan` | 江南大学 | `fzu` | 福州大学 |
| `hqu` | 华侨大学 | `ncu` | 南昌大学 |
| `gxu` | 广西大学 | `ynu` | 云南大学 |
| `gzu` | 贵州大学 | `xju` | 新疆大学 |
| `imu` | 内蒙古大学 | `nxu` | 宁夏大学 |

#### 港澳台高校（8所）

| 标识符 | 机构 | 域名 |
|--------|------|------|
| `hku` | 香港大学 | hku.hk |
| `usthk` | 香港科技大学 | ust.hk |
| `cuhk` | 香港中文大学 | cuhk.edu.hk |
| `cityu` | 香港城市大学 | cityu.edu.hk |
| `polyu` | 香港理工大学 | polyu.edu.hk |
| `hkbu` | 香港浸会大学 | hkbu.edu.hk |
| `umac` | 澳门大学 | um.edu.mo |
| `ntu` | 台湾大学 | ntu.edu.tw |

> **提示**: 如果你的学校不在列表中，可以编辑 `campus_access_tool.py` 中的 `INSTITUTION_DOMAINS` 字典添加。

## 使用方法

### 在 Claude Code 中使用

安装配置后，可以直接在 Claude Code 中使用：

```
用户: 搜索 attention mechanism 相关论文
AI: [调用 search_arxiv 工具，返回论文列表]

用户: 通过校园网访问这篇 IEEE 论文
AI: [调用 access_paper 工具，检测 PDF 可用性]

用户: 检测校园网连接状态
AI: [调用 check_campus_connection 工具]
```

### 使用 Skill

本仓库包含一个 Claude Code Skill，可以提供更完整的体验：

```bash
# 将 skill.md 复制到 Claude Code skills 目录
cp skill.md ~/.claude/skills/paper-search/
```

然后使用 `/paper-search` 命令调用。

## MCP 工具列表

### paper-search MCP

| 工具 | 功能 | 参数 |
|------|------|------|
| `search_arxiv` | 搜索 arXiv 论文 | `query`, `max_results` |
| `search_pubmed` | 搜索 PubMed 论文 | `query`, `max_results` |
| `search_google_scholar` | 搜索 Google Scholar | `query`, `max_results` |
| `download_arxiv` | 下载 arXiv PDF | `arxiv_id` |
| `read_arxiv_paper` | 读取论文内容 | `arxiv_id` |

### campus-access MCP

| 工具 | 功能 | 参数 |
|------|------|------|
| `check_campus_connection` | 检测校园网状态 | - |
| `search_database` | 搜索机构数据库 | `database`, `query`, `max_results` |
| `access_paper` | 访问论文页面 | `url`, `database` |
| `download_pdf` | 下载 PDF | `url`, `paper_title` |
| `list_databases` | 列出支持的数据库 | - |

## 示例

### 搜索论文

```python
# 使用 MCP 工具搜索 arXiv
result = search_arxiv(query="transformer attention", max_results=10)

# 返回结果示例
{
  "papers": [
    {
      "title": "Attention Is All You Need",
      "authors": ["Ashish Vaswani", "Noam Shazeer", ...],
      "abstract": "The dominant sequence transduction models...",
      "pdf_url": "https://arxiv.org/pdf/1706.03762",
      "arxiv_id": "1706.03762"
    }
  ]
}
```

### 校园网访问

```python
# 检测校园网连接
status = check_campus_connection()
# {"is_connected": True, "institution": "neu", "accessible_databases": ["ieee", "springer", ...]}

# 访问 IEEE 论文
result = access_paper("https://ieeexplore.ieee.org/document/12345", database="ieee")
# {"success": True, "has_pdf": True, "pdf_url": "https://ieeexplore.ieee.org/stamp/..."}
```

## 项目结构

```
paper-search-mcp/
├── README.md                   # 本文档
├── run_paper_search_mcp.py     # 论文搜索 MCP 服务器
├── campus_access_tool.py       # 校园网访问核心模块
├── campus_mcp_server.py        # 校园网访问 MCP 服务器
├── test_mcp_e2e.py            # 端到端测试脚本
├── claude_settings.json       # Claude Code 配置示例
├── skill.md                    # Claude Code Skill 定义
└── requirements.txt           # Python 依赖
```

## 测试

运行端到端测试：

```bash
# 激活虚拟环境
venv\Scripts\activate

# 运行测试
python test_mcp_e2e.py
```

## 错误处理

本工具内置了常见错误的自动修复机制：

| 错误类型 | 症状 | 自动修复 |
|----------|------|----------|
| 模块导入失败 | `ModuleNotFoundError: No module named 'paper_search_mcp'` | 自动使用虚拟环境 Python |
| 编码错误 | `UnicodeDecodeError: 'gbk' codec can't decode` | 强制 UTF-8 编码 |
| 代理解析失败 | `Failed to resolve 'xxx.proxy.edu.cn'` | 直接访问原 URL |

## 常见问题

### Q: 为什么搜索结果为空？

A: 可能是网络问题或 API 限流。请检查网络连接，或稍后重试。

### Q: 校园网访问失败怎么办？

A: 确保你在校园网环境下。如果使用 VPN，可能需要配置代理。部分学校可能需要通过图书馆网站登录。

### Q: 如何添加新的机构支持？

A: 编辑 `campus_access_tool.py`，在 `INSTITUTION_DOMAINS` 字典中添加机构标识符和域名。

## 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 许可证

MIT License

## 致谢

- [paper-search-mcp](https://pypi.org/project/paper-search-mcp/) - 论文搜索核心库
- [MCP](https://modelcontextprotocol.io/) - Model Context Protocol
- [Claude Code](https://claude.ai/code) - Anthropic 的 AI 编程助手
