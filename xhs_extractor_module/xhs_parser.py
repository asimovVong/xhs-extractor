# xhs_parser.py
"""
小红书笔记解析器
从小红书链接或 HTML 中提取笔记内容（文本 + 图片）
"""
from __future__ import annotations

import re
import json
import uuid
from typing import List, Optional
from urllib.parse import urlparse, parse_qs

import requests
from bs4 import BeautifulSoup

from .models import Note


def extract_note_id_from_url(url: str) -> Optional[str]:
    """
    从小红书链接中提取 note_id
    支持多种格式：
    - http://xhslink.com/... (短链接，需要先解析)
    - https://www.xiaohongshu.com/explore/xxxxx
    - https://www.xiaohongshu.com/user/xxx/xxxxx
    """
    # 如果是短链接，先访问获取真实链接
    if "xhslink.com" in url:
        try:
            response = requests.head(url, allow_redirects=True, timeout=10)
            url = response.url
        except Exception as e:
            print(f"警告：无法解析短链接 {url}: {e}")
            return None
    
    # 从 URL 中提取 note_id
    patterns = [
        r'/explore/([a-f0-9]+)',
        r'/discovery/item/([a-f0-9]+)',
        r'/user/[^/]+/([a-f0-9]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def fetch_xhs_note(url: str, cookies: Optional[dict] = None, cookie_string: Optional[str] = None) -> Note:
    """
    从小红书链接获取笔记内容
    
    Args:
        url: 小红书笔记链接
        cookies: 可选，如果需要登录才能查看的内容，可以提供 cookies
    
    Returns:
        Note 对象
    
    Note:
        小红书内容可能需要登录才能查看。如果提取失败，建议：
        1. 手动复制笔记内容到文件，使用 parse_note_from_file 函数
        2. 或者在浏览器中登录后，获取 cookies 传入此函数
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://www.xiaohongshu.com/',
        'Origin': 'https://www.xiaohongshu.com',
    }
    
    # 如果提供了 Cookie 字符串（从 Network 面板复制），直接使用
    if cookie_string:
        headers['Cookie'] = cookie_string
        cookies = None  # 不使用 cookies 参数，改用 header
    
    try:
        # 如果没有 cookie，缩短超时时间（快速失败）
        timeout = 3 if not cookie_string and not cookies else 15
        response = requests.get(url, headers=headers, cookies=cookies, timeout=timeout)
        response.raise_for_status()
        html = response.text
    except Exception as e:
        raise ValueError(f"无法获取小红书页面: {e}")
    
    # 解析 HTML
    soup = BeautifulSoup(html, 'html.parser')
    
    # 尝试从 __INITIAL_STATE__ 中提取数据
    initial_state = None
    for script in soup.find_all('script'):
        if script.string and '__INITIAL_STATE__' in script.string:
            # 提取 JSON 数据
            match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.+?})\s*</script>', script.string, re.DOTALL)
            if match:
                try:
                    initial_state = json.loads(match.group(1))
                except json.JSONDecodeError:
                    pass
            break
    
    note_id = extract_note_id_from_url(url) or str(uuid.uuid4())
    title = ""
    text = ""
    images = []
    raw = {"url": url, "html_length": len(html)}
    
    if initial_state:
        # 从 __INITIAL_STATE__ 中提取笔记数据
        try:
            # 根据小红书的数据结构提取（可能需要根据实际结构调整）
            note_data = initial_state.get('note', {}) or initial_state.get('noteDetail', {})
            if not note_data:
                # 尝试从其他路径查找
                for key in initial_state.keys():
                    if 'note' in key.lower():
                        note_data = initial_state[key]
                        break
            
            if note_data:
                title = note_data.get('title', '') or note_data.get('noteCard', {}).get('displayTitle', '')
                text = note_data.get('desc', '') or note_data.get('content', '')
                
                # 改进图片提取逻辑，支持多种数据结构
                image_list = note_data.get('imageList', []) or note_data.get('images', []) or []
                images = []
                for img in image_list:
                    if not img:
                        continue
                    # 尝试多种路径获取图片 URL
                    img_url = None
                    if isinstance(img, str):
                        # 如果直接是字符串 URL
                        img_url = img
                    elif isinstance(img, dict):
                        # 尝试多种可能的字段
                        img_url = (
                            img.get('url') or 
                            img.get('urlDefault') or 
                            img.get('picUrl') or 
                            img.get('info', {}).get('url') or
                            img.get('info', {}).get('urlDefault') or
                            img.get('info', {}).get('picUrl') or
                            img.get('imageInfo', {}).get('url') or
                            img.get('imageInfo', {}).get('urlDefault')
                        )
                    
                    if img_url and img_url.startswith('http'):
                        if img_url not in images:  # 去重
                            images.append(img_url)
                
                raw['initial_state'] = note_data
                raw['extracted_images_count'] = len(images)
        except Exception as e:
            print(f"警告：解析 __INITIAL_STATE__ 时出错: {e}")
    
    # 如果从 __INITIAL_STATE__ 没有获取到数据，尝试从 HTML 中直接提取
    if not text:
        # 尝试多种方式查找内容
        # 方法1: 查找常见的内容容器
        content_selectors = [
            'div[class*="content"]',
            'div[class*="note"]',
            'div[class*="desc"]',
            'div[class*="text"]',
            'div[class*="detail"]',
            '.note-detail',
            '.note-content',
        ]
        
        for selector in content_selectors:
            try:
                content_div = soup.select_one(selector)
                if content_div:
                    text = content_div.get_text(strip=True)
                    if len(text) > 20:  # 确保提取到有效内容
                        break
            except:
                continue
        
        # 方法2: 查找所有包含文本的 div
        if not text or len(text) < 20:
            for div in soup.find_all('div'):
                div_text = div.get_text(strip=True)
                # 过滤掉导航、按钮等短文本
                if len(div_text) > 50 and '登录' not in div_text and '注册' not in div_text:
                    text = div_text
                    break
        
        # 查找标题
        if not title or len(title) < 5:
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text(strip=True)
        
        # 查找图片
        if not images:
            img_tags = soup.find_all('img')
            for img in img_tags:
                src = img.get('src') or img.get('data-src') or img.get('data-lazy') or img.get('data-original')
                if src:
                    # 过滤掉小图标、logo等
                    if any(keyword in src.lower() for keyword in ['sns', 'xhslink', 'xiaohongshu', 's3', 'cdn']):
                        if src.startswith('//'):
                            src = 'https:' + src
                        if src.startswith('http') and src not in images:
                            images.append(src)
    
    # 清理文本
    text = text.strip()
    
    # 检查是否需要登录
    login_keywords = ['登录', '注册', '发现发布通知登录我', '请登录', '登录查看']
    if not text or len(text) < 20 or any(keyword in text for keyword in login_keywords):
        print("⚠ 警告：检测到可能需要登录才能查看完整内容")
        print("   提取到的文本可能不完整，建议：")
        print("   1. 在浏览器中打开链接，复制完整内容到文件")
        print("   2. 使用命令: python main.py ingest <文件路径>")
        print("   3. 或者在浏览器中登录后，获取 cookies 传入解析函数")
    
    if not title or len(title) < 5:
        # 尝试从文本第一行提取标题
        lines = text.split('\n')
        if lines:
            title = lines[0][:100].strip()
    
    return Note(
        id=note_id,
        url=url,
        title=title or "未命名笔记",
        text=text,
        ocr_text="",  # OCR 文本由后续的 OCR 步骤填充
        images=images,
        raw=raw,
    )


def parse_note_from_file(file_path: str, url: Optional[str] = None) -> Note:
    """
    从本地文件读取笔记内容（用于测试）
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 尝试提取标题（第一行）
    lines = content.split('\n')
    title = lines[0].strip() if lines else "本地笔记"
    
    return Note(
        id=str(uuid.uuid4()),
        url=url or f"file://{file_path}",
        title=title,
        text=content,
        ocr_text="",
        images=[],
        raw={"source": "local_file", "file_path": file_path},
    )


if __name__ == "__main__":
    # 测试：从文件读取
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1].startswith("http"):
            # 从 URL 解析
            note = fetch_xhs_note(sys.argv[1])
        else:
            # 从文件解析
            note = parse_note_from_file(sys.argv[1])
        
        print(f"标题: {note.title}")
        print(f"文本长度: {len(note.text)}")
        print(f"图片数量: {len(note.images)}")
        print(f"\n文本预览:\n{note.text[:500]}...")

