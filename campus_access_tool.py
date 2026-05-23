"""校园网机构访问工具模块

功能：
    利用校园网环境访问付费论文数据库和期刊文章。
    在校园网环境下可直接访问机构订阅的资源。

支持的平台：
    - IEEE Xplore
    - ACM Digital Library
    - SpringerLink
    - Elsevier/ScienceDirect
    - Wiley Online Library
    - 中国知网 (CNKI)
    - 万方数据

使用前提：
    用户必须在校园网环境下。
"""

import os
import re
import json
import time
import logging
from urllib.parse import urlparse, urljoin
from typing import Optional, Dict, List, Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# 机构域名映射
INSTITUTION_DOMAINS = {
    "neu": "neu.edu.cn",
    "tsinghua": "tsinghua.edu.cn",
    "pku": "pku.edu.cn",
    "sjtu": "sjtu.edu.cn",
    "fudan": "fudan.edu.cn",
    "zju": "zju.edu.cn",
    "ustc": "ustc.edu.cn",
    "hit": "hit.edu.cn",
    "buaa": "buaa.edu.cn",
    "nju": "nju.edu.cn",
}

# 东北大学图书馆代理配置
NEU_LIBRARY_PROXY = "https://lib.neu.edu.cn"

# 常见学术数据库配置
DATABASE_CONFIGS = {
    "ieee": {
        "name": "IEEE Xplore",
        "base": "ieeexplore.ieee.org",
        "search_url": "https://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true&queryText={query}",
        "pdf_pattern": "/stamp/stamp.jsp?tp=&arnumber={id}",
    },
    "acm": {
        "name": "ACM Digital Library",
        "base": "dl.acm.org",
        "search_url": "https://dl.acm.org/action/doSearch?AllField={query}",
    },
    "springer": {
        "name": "SpringerLink",
        "base": "link.springer.com",
        "search_url": "https://link.springer.com/search?query={query}",
    },
    "elsevier": {
        "name": "ScienceDirect",
        "base": "sciencedirect.com",
        "search_url": "https://www.sciencedirect.com/search?qs={query}",
    },
    "wiley": {
        "name": "Wiley Online Library",
        "base": "onlinelibrary.wiley.com",
        "search_url": "https://onlinelibrary.wiley.com/action/doSearch?AllField={query}",
    },
    "cnki": {
        "name": "中国知网",
        "base": "cnki.net",
        "search_url": "https://www.cnki.net/",
        "direct_access": True,  # 校园网直接访问
    },
    "wanfang": {
        "name": "万方数据",
        "base": "wanfangdata.com.cn",
        "search_url": "https://www.wanfangdata.com.cn/search",
        "direct_access": True,
    },
}

# EZProxy 格式的代理 URL 模式（如果学校使用 EZProxy）
EZPROXY_PATTERNS = [
    "{base_url}.{proxy_domain}",  # 域名替换模式
    "{proxy_url}/login?url={original_url}",  # 登录跳转模式
]


class CampusAccessTool:
    """校园网机构访问工具"""

    def __init__(self, institution: str = "neu"):
        self.institution = institution
        self.institution_domain = INSTITUTION_DOMAINS.get(institution, f"{institution}.edu.cn")
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """创建请求会话"""
        session = requests.Session()

        # 重试策略
        retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # 设置浏览器 User-Agent
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        })

        return session

    def check_campus_connection(self) -> Dict[str, Any]:
        """检测校园网连接状态"""
        result = {
            "is_connected": False,
            "institution": self.institution,
            "institution_domain": self.institution_domain,
            "accessible_databases": [],
            "library_url": None,
        }

        # 尝试访问学校官网
        try:
            resp = self.session.get(f"https://www.{self.institution_domain}", timeout=10)
            result["is_connected"] = resp.status_code == 200
        except Exception:
            pass

        # 尝试访问图书馆
        library_urls = [
            f"https://lib.{self.institution_domain}",
            f"https://library.{self.institution_domain}",
            f"https://www.{self.institution_domain}/library",
        ]
        for url in library_urls:
            try:
                resp = self.session.get(url, timeout=5, allow_redirects=True)
                if resp.status_code == 200:
                    result["library_url"] = resp.url
                    break
            except Exception:
                pass

        # 检测可访问的数据库
        for db_name, db_config in DATABASE_CONFIGS.items():
            try:
                resp = self.session.get(f"https://{db_config['base']}", timeout=5)
                if resp.status_code == 200:
                    result["accessible_databases"].append(db_name)
            except Exception:
                pass

        return result

    def get_database_search_url(self, database: str, query: str) -> str:
        """获取数据库搜索 URL"""
        if database not in DATABASE_CONFIGS:
            return None
        return DATABASE_CONFIGS[database]["search_url"].format(query=query)

    def search_database(self, database: str, query: str, max_results: int = 10) -> Dict[str, Any]:
        """搜索数据库"""
        result = {
            "database": database,
            "query": query,
            "success": False,
            "papers": [],
            "message": "",
            "search_url": None,
        }

        if database not in DATABASE_CONFIGS:
            result["message"] = f"不支持的数据库: {database}，支持: {list(DATABASE_CONFIGS.keys())}"
            return result

        db_config = DATABASE_CONFIGS[database]
        search_url = self.get_database_search_url(database, query)
        result["search_url"] = search_url

        try:
            resp = self.session.get(search_url, timeout=30, allow_redirects=True)
            result["http_status"] = resp.status_code

            if resp.status_code == 200:
                # 解析搜索结果
                papers = self._parse_results(resp.text, database, db_config["base"])
                result["papers"] = papers[:max_results]
                result["success"] = True
                result["message"] = f"找到 {len(papers)} 篇论文"
            else:
                result["message"] = f"HTTP {resp.status_code}"

        except Exception as e:
            result["message"] = str(e)

        return result

    def _parse_results(self, html: str, database: str, base_domain: str) -> List[Dict]:
        """解析搜索结果"""
        papers = []

        # 通用标题提取
        patterns = [
            r'<h[23][^>]*>\s*<a[^>]*href="([^"]*)"[^>]*>([^<]+)</a>',
            r'<a[^>]*class="[^"]*title[^"]*"[^>]*href="([^"]*)"[^>]*>([^<]+)</a>',
            r'<div[^>]*class="[^"]*result-item[^"]*"[^>]*>.*?<a[^>]*href="([^"]*)"[^>]*>([^<]+)</a>',
        ]

        seen = set()
        for pattern in patterns:
            matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)
            for url, title in matches:
                title = title.strip()
                # 过滤无效标题
                if len(title) < 10 or title.lower() in seen:
                    continue
                seen.add(title.lower())

                # 构建完整 URL
                if not url.startswith("http"):
                    url = f"https://{base_domain}{url}"

                papers.append({
                    "title": title,
                    "url": url,
                    "source": DATABASE_CONFIGS.get(database, {}).get("name", database),
                })

                if len(papers) >= 20:
                    return papers

        return papers

    def access_paper(self, url: str, database: str = None) -> Dict[str, Any]:
        """访问论文页面"""
        result = {
            "original_url": url,
            "success": False,
            "content_type": None,
            "has_pdf": False,
            "pdf_url": None,
            "message": "",
        }

        # 自动检测数据库
        if not database:
            for db_name, db_config in DATABASE_CONFIGS.items():
                if db_config["base"] in url:
                    database = db_name
                    break

        try:
            resp = self.session.get(url, timeout=30, allow_redirects=True)
            result["success"] = resp.status_code == 200
            result["content_type"] = resp.headers.get("Content-Type", "")
            result["message"] = f"HTTP {resp.status_code}"

            # 检查是否是 PDF
            if "pdf" in result["content_type"].lower():
                result["has_pdf"] = True
                result["pdf_url"] = url
                result["pdf_size"] = len(resp.content)
            else:
                # 尝试提取 PDF 链接
                pdf_links = self._extract_pdf_links(resp.text, url)
                if pdf_links:
                    result["has_pdf"] = True
                    result["pdf_url"] = pdf_links[0]

        except Exception as e:
            result["message"] = str(e)

        return result

    def _extract_pdf_links(self, html: str, base_url: str) -> List[str]:
        """提取 PDF 链接"""
        pdf_links = []

        patterns = [
            r'href="([^"]*\.pdf[^"]*)"',
            r'"pdfUrl"\s*:\s*"([^"]*)"',
            r'"pdf"\s*:\s*"([^"]*)"',
            r'content="([^"]*\.pdf[^"]*)"',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                if match.startswith("http"):
                    pdf_links.append(match)
                elif match.startswith("/"):
                    parsed = urlparse(base_url)
                    pdf_links.append(f"{parsed.scheme}://{parsed.netloc}{match}")

        return list(set(pdf_links))

    def download_pdf(self, url: str, save_path: str = None, paper_title: str = None) -> Dict[str, Any]:
        """下载 PDF"""
        result = {
            "success": False,
            "url": url,
            "save_path": None,
            "file_size": 0,
            "message": "",
        }

        try:
            resp = self.session.get(url, timeout=60, allow_redirects=True)

            if resp.status_code != 200:
                result["message"] = f"HTTP {resp.status_code}"
                return result

            content_type = resp.headers.get("Content-Type", "")

            # 如果不是 PDF，尝试提取 PDF 链接
            if "pdf" not in content_type.lower():
                pdf_links = self._extract_pdf_links(resp.text, url)
                if pdf_links:
                    resp = self.session.get(pdf_links[0], timeout=60)
                    content_type = resp.headers.get("Content-Type", "")

            if "pdf" in content_type.lower():
                pdf_content = resp.content

                # 生成保存路径
                if not save_path:
                    if paper_title:
                        safe_title = re.sub(r'[^\w\s-]', '', paper_title)
                        safe_title = re.sub(r'[\s]+', '_', safe_title)
                        filename = f"{safe_title[:80]}.pdf"
                    else:
                        url_id = re.search(r'[\d]+', url)
                        filename = f"paper_{url_id.group() if url_id else 'unknown'}.pdf"
                    save_path = os.path.join(os.getcwd(), "downloads", filename)

                # 确保目录存在
                os.makedirs(os.path.dirname(save_path), exist_ok=True)

                with open(save_path, "wb") as f:
                    f.write(pdf_content)

                result["success"] = True
                result["save_path"] = save_path
                result["file_size"] = len(pdf_content)
                result["message"] = "下载成功"
            else:
                result["message"] = "未找到 PDF 内容"

        except Exception as e:
            result["message"] = str(e)

        return result


# 全局实例
campus_tool = CampusAccessTool()


def check_campus_connection() -> Dict[str, Any]:
    return campus_tool.check_campus_connection()


def search_database(database: str, query: str, max_results: int = 10) -> Dict[str, Any]:
    return campus_tool.search_database(database, query, max_results)


def access_paper(url: str, database: str = None) -> Dict[str, Any]:
    return campus_tool.access_paper(url, database)


def download_pdf(url: str, save_path: str = None, paper_title: str = None) -> Dict[str, Any]:
    return campus_tool.download_pdf(url, save_path, paper_title)


# 兼容旧接口
def access_via_institution(url: str, database: str = None) -> Dict[str, Any]:
    return access_paper(url, database)


def download_paper_pdf(url: str, database: str = None, save_path: str = None, paper_title: str = None) -> Dict[str, Any]:
    return download_pdf(url, save_path, paper_title)


def search_institution_database(database: str, query: str, max_results: int = 10) -> Dict[str, Any]:
    return search_database(database, query, max_results)


DATABASE_PROXY_PATTERNS = {k: {"base": v["base"]} for k, v in DATABASE_CONFIGS.items()}


__all__ = [
    "CampusAccessTool",
    "check_campus_connection",
    "search_database",
    "access_paper",
    "download_pdf",
    "access_via_institution",
    "download_paper_pdf",
    "search_institution_database",
    "DATABASE_CONFIGS",
    "DATABASE_PROXY_PATTERNS",
    "INSTITUTION_DOMAINS",
]