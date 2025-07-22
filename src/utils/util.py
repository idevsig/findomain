from __future__ import annotations

import re
from datetime import datetime
from urllib.parse import urlparse
from urllib.parse import urlunparse


def is_valid_url(url: str) -> bool:
    """
    检查 URL 是否合法
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def replace_url_at(url: str, date_str: str = "") -> str:
    """
    替换除 schema 和 hostname 部分外的 @ 为日期
    """
    # 获取当前日期
    date_str = date_str or datetime.now().strftime("%Y%m%d%H%M%S")

    parsed = urlparse(url)

    # 检测 @ 是否在 netloc（hostname/userinfo）部分
    if "@" in parsed.netloc:
        return url  # 如果在 hostname 中含 @，不处理

    # 替换 path 中的 @ 为 {date}
    def replace_func(match):
        return f"{date_str}{match.group(1)}"

    new_path = re.sub(r"@([a-zA-Z0-9_\-\.]+)", replace_func, parsed.path)

    # 构建新 URL
    new_parsed = parsed._replace(path=new_path)
    return urlunparse(new_parsed)
