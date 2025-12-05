# xhs_share.py
"""
小红书分享文本解析模块
从分享文案中提取短链接
"""
from __future__ import annotations

import re
from typing import Optional


def extract_xhs_url_from_share_text(text: str) -> Optional[str]:
    """
    从小红书分享文案中提取 http(s) 开头的链接（一般是 xhslink 的短链）。
    
    Args:
        text: 小红书分享文案，例如：
            "算法面经：字节大模型Agent 11.16 一面： 请介绍 Tran... http://xhslink.com/o/EEfBYaRn4M 复制后打开【小红书】查看笔记！"
    
    Returns:
        提取到的URL字符串，如果未找到则返回None
    
    Example:
        >>> text = "算法面经：字节大模型Agent 11.16 一面： 请介绍 Tran... http://xhslink.com/o/EEfBYaRn4M 复制后打开【小红书】查看笔记！"
        >>> extract_xhs_url_from_share_text(text)
        'http://xhslink.com/o/EEfBYaRn4M'
    """
    if not text:
        return None
    
    # 找第一个 http 开头的 URL
    # 先匹配完整的URL（包括路径、查询参数等），直到遇到空白或明显的中文标点
    # URL可能包含的字符：字母、数字、-._~:/?#[]@!$&'()*+,;=
    # 但遇到中文标点符号时应该停止
    m = re.search(r"(https?://[^\s）)＞》>，,。\n\r\t]+)", text)
    if not m:
        return None
    
    url = m.group(1).strip()
    
    # 清理末尾可能的标点符号（中文和英文）
    # 注意：点号可能是URL的一部分（如.com），所以只清理末尾的标点
    url = url.rstrip("）)＞》>，,。\n\r\t")
    
    # 如果URL以点号结尾（且不是.com/.cn等域名后缀），可能是误匹配，需要进一步处理
    # 但通常URL不会以点号结尾，所以这里先简单处理
    
    return url


if __name__ == "__main__":
    # 测试
    test_text = "算法面经：字节大模型Agent 11.16 一面： 请介绍 Tran... http://xhslink.com/o/EEfBYaRn4M 复制后打开【小红书】查看笔记！"
    url = extract_xhs_url_from_share_text(test_text)
    print(f"提取到的URL: {url}")

