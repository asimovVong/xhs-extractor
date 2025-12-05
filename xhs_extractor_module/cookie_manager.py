# cookie_manager.py
"""
Cookie 管理模块
处理小红书 Cookie 的保存、加载和解析
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, Dict


class CookieManager:
    """Cookie 管理器"""
    
    def __init__(self, cookie_dir: str = "cookies"):
        """
        Args:
            cookie_dir: Cookie 文件保存目录
        """
        self.cookie_dir = Path(cookie_dir)
        self.cookie_file = self.cookie_dir / "xhs_cookies_latest.json"
    
    def parse_cookie_string(self, cookie_str: str) -> Dict[str, str]:
        """
        将浏览器 Network 面板复制的 Cookie 字符串转换为字典
        
        Args:
            cookie_str: Cookie 字符串，格式如 "key1=value1; key2=value2"
        
        Returns:
            Cookie 字典
        """
        cookies = {}
        if not cookie_str:
            return cookies
        
        # 去除可能的前缀（如 "Cookie: " 或 "cookie: "）
        cookie_str = cookie_str.strip()
        if cookie_str.lower().startswith('cookie:'):
            cookie_str = cookie_str[7:].strip()
        
        # 按分号分割
        for item in cookie_str.split(';'):
            item = item.strip()
            if '=' in item:
                key, value = item.split('=', 1)
                cookies[key.strip()] = value.strip()
        
        return cookies
    
    def load_saved_cookies(self) -> Optional[Dict[str, str]]:
        """
        加载已保存的 Cookie
        
        Returns:
            Cookie 字典，如果不存在则返回 None
        """
        if self.cookie_file.exists():
            try:
                with open(self.cookie_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return None
    
    def save_cookies(self, cookies: Dict[str, str]):
        """
        保存 Cookie 到文件
        
        Args:
            cookies: Cookie 字典
        """
        if not cookies:
            return
        
        self.cookie_dir.mkdir(exist_ok=True)
        
        with open(self.cookie_file, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, ensure_ascii=False, indent=2)
    
    def cookie_dict_to_string(self, cookies: Dict[str, str]) -> str:
        """
        将 Cookie 字典转换为字符串格式（用于 HTTP Header）
        
        Args:
            cookies: Cookie 字典
        
        Returns:
            Cookie 字符串，格式如 "key1=value1; key2=value2"
        """
        return "; ".join([f"{key}={value}" for key, value in cookies.items()])


if __name__ == "__main__":
    # 测试
    manager = CookieManager()
    
    # 测试解析
    test_cookie_str = "a1=xxx; web_session=yyy; webId=zzz"
    parsed = manager.parse_cookie_string(test_cookie_str)
    print(f"解析结果: {parsed}")
    
    # 测试保存和加载
    manager.save_cookies(parsed)
    loaded = manager.load_saved_cookies()
    print(f"加载结果: {loaded}")
    
    # 测试转换回字符串
    cookie_str = manager.cookie_dict_to_string(loaded)
    print(f"Cookie 字符串: {cookie_str}")

