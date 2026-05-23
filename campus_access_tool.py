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

# 机构域名映射（39所985高校 + 其他重点院校）
INSTITUTION_DOMAINS = {
    # 39所985高校
    "pku": "pku.edu.cn",                    # 北京大学
    "tsinghua": "tsinghua.edu.cn",          # 清华大学
    "fudan": "fudan.edu.cn",                # 复旦大学
    "sjtu": "sjtu.edu.cn",                  # 上海交通大学
    "zju": "zju.edu.cn",                    # 浙江大学
    "ustc": "ustc.edu.cn",                  # 中国科学技术大学
    "nju": "nju.edu.cn",                    # 南京大学
    "hit": "hit.edu.cn",                    # 哈尔滨工业大学
    "buaa": "buaa.edu.cn",                  # 北京航空航天大学
    "neu": "neu.edu.cn",                    # 东北大学
    "tju": "tju.edu.cn",                    # 天津大学
    "nankai": "nankai.edu.cn",              # 南开大学
    "dlut": "dlut.edu.cn",                  # 大连理工大学
    "jlu": "jlu.edu.cn",                    # 吉林大学
    "hit-wh": "hitwh.edu.cn",               # 哈尔滨工业大学(威海)
    "tongji": "tongji.edu.cn",              # 同济大学
    "seu": "seu.edu.cn",                    # 东南大学
    "zju": "zju.edu.cn",                    # 浙江大学
    "ustc": "ustc.edu.cn",                  # 中国科学技术大学
    "xmu": "xmu.edu.cn",                    # 厦门大学
    "sdust": "sdust.edu.cn",                # 山东大学
    "ouc": "ouc.edu.cn",                    # 中国海洋大学
    "whu": "whu.edu.cn",                    # 武汉大学
    "hust": "hust.edu.cn",                  # 华中科技大学
    "csu": "csu.edu.cn",                    # 中南大学
    "scut": "scut.edu.cn",                  # 华南理工大学
    "sysu": "sysu.edu.cn",                  # 中山大学
    "sicau": "sicau.edu.cn",                # 四川大学
    "uestc": "uestc.edu.cn",                # 电子科技大学
    "cqu": "cqu.edu.cn",                    # 重庆大学
    "xjtu": "xjtu.edu.cn",                  # 西安交通大学
    "nwpu": "nwpu.edu.cn",                  # 西北工业大学
    "nwsuaf": "nwsuaf.edu.cn",              # 西北农林科技大学
    "lzu": "lzu.edu.cn",                    # 兰州大学
    "bnu": "bnu.edu.cn",                    # 北京师范大学
    "ruc": "ruc.edu.cn",                    # 中国人民大学
    "bju": "bju.edu.cn",                    # 北京理工大学
    "cau": "cau.edu.cn",                    # 中国农业大学
    "cuc": "cuc.edu.cn",                    # 中央民族大学
    "nwu": "nwu.edu.cn",                    # 西北大学
    # 其他重点院校（211高校等）
    "bjtu": "bjtu.edu.cn",                  # 北京交通大学
    "bupt": "bupt.edu.cn",                  # 北京邮电大学
    "cug": "cug.edu.cn",                    # 中国地质大学
    "cumt": "cumt.edu.cn",                  # 中国矿业大学
    "hohai": "hohai.edu.cn",                # 河海大学
    "njau": "njau.edu.cn",                  # 南京农业大学
    "njfu": "njfu.edu.cn",                  # 南京林业大学
    "njtech": "njtech.edu.cn",              # 南京工业大学
    "nuaa": "nuaa.edu.cn",                  # 南京航空航天大学
    "nuist": "nuist.edu.cn",                # 南京信息工程大学
    "njust": "njust.edu.cn",                # 南京理工大学
    "scu": "scu.edu.cn",                    # 四川大学
    "swjtu": "swjtu.edu.cn",                # 西南交通大学
    "uestc": "uestc.edu.cn",                # 电子科技大学
    "cdu": "cdu.edu.cn",                    # 成都大学
    "gdut": "gdut.edu.cn",                  # 广东工业大学
    "szu": "szu.edu.cn",                    # 深圳大学
    "hnu": "hnu.edu.cn",                    # 湖南大学
    "nudt": "nudt.edu.cn",                  # 国防科技大学
    "ccnu": "ccnu.edu.cn",                  # 华中师范大学
    "whut": "whut.edu.cn",                  # 武汉理工大学
    "hust": "hust.edu.cn",                  # 华中科技大学
    "wust": "wust.edu.cn",                  # 武汉科技大学
    "ecust": "ecust.edu.cn",                # 华东理工大学
    "shu": "shu.edu.cn",                    # 上海大学
    "ecnu": "ecnu.edu.cn",                  # 华东师范大学
    "suda": "suda.edu.cn",                  # 苏州大学
    "jiangnan": "jiangnan.edu.cn",          # 江南大学
    "zstu": "zstu.edu.cn",                  # 浙江理工大学
    "hdu": "hdu.edu.cn",                    # 杭州电子科技大学
    "cqupt": "cqupt.edu.cn",                # 重庆邮电大学
    "swufe": "swufe.edu.cn",                # 西南财经大学
    "sdufe": "sdufe.edu.cn",                # 山东财经大学
    "hnust": "hnust.edu.cn",                # 湖南科技大学
    "xtu": "xtu.edu.cn",                    # 湘潭大学
    "nchu": "nchu.edu.cn",                  # 南昌大学
    "jxnu": "jxnu.edu.cn",                  # 江西师范大学
    "fzu": "fzu.edu.cn",                    # 福州大学
    "hqu": "hqu.edu.cn",                    # 华侨大学
    "gxu": "gxu.edu.cn",                    # 广西大学
    "gxnu": "gxnu.edu.cn",                  # 广西师范大学
    "ynu": "ynu.edu.cn",                    # 云南大学
    "kmust": "kmust.edu.cn",                # 昆明理工大学
    "gzu": "gzu.edu.cn",                    # 贵州大学
    "swun": "swun.edu.cn",                  # 西南民族大学
    "xju": "xju.edu.cn",                    # 新疆大学
    "nmg": "imu.edu.cn",                    # 内蒙古大学
    "qhnu": "qhnu.edu.cn",                  # 青海师范大学
    "nxu": "nxu.edu.cn",                    # 宁夏大学
    # 香港、澳门、台湾地区高校
    "hku": "hku.hk",                        # 香港大学
    "usthk": "ust.hk",                      # 香港科技大学
    "cuhk": "cuhk.edu.hk",                  # 香港中文大学
    "cityu": "cityu.edu.hk",                # 香港城市大学
    "polyu": "polyu.edu.hk",                # 香港理工大学
    "hkbu": "hkbu.edu.hk",                  # 香港浸会大学
    "umac": "um.edu.mo",                    # 澳门大学
    "must": "must.edu.mo",                  # 澳门科技大学
    "ntu": "ntu.edu.tw",                    # 台湾大学
    "nthu": "nthu.edu.tw",                  # 台湾清华大学
    "nctu": "nctu.edu.tw",                  # 台湾交通大学
    "ncku": "ncku.edu.tw",                  # 台湾成功大学
}

# 东北大学图书馆代理配置（示例）
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