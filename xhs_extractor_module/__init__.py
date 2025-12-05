# xhs_extractor_module
"""
小红书笔记提取模块

提供两种方式提取小红书笔记内容：
1. Playwright 版本（推荐）：自动登录，无需手动管理 Cookie
2. requests 版本：轻量级，需要手动管理 Cookie
"""

# Playwright 版本（推荐）
from .xhs_share import extract_xhs_url_from_share_text
from .xhs_login import login_xhs_and_save_state, check_login_state_exists, STATE_PATH
from .xhs_fetch import fetch_note_from_share_text, fetch_note_from_url, _parse_note_from_state

# 基础版本
from .xhs_parser import fetch_xhs_note, extract_note_id_from_url, parse_note_from_file
from .cookie_manager import CookieManager

# 数据模型
from .models import Note, InterviewQuestion

# OCR（可选）
try:
    from .ocr import OCRProcessor, extract_ocr_from_note
except ImportError:
    # OCR 模块可能未安装依赖
    pass

__all__ = [
    # Playwright 版本
    "extract_xhs_url_from_share_text",
    "login_xhs_and_save_state",
    "check_login_state_exists",
    "STATE_PATH",
    "fetch_note_from_share_text",
    "fetch_note_from_url",
    # 基础版本
    "fetch_xhs_note",
    "extract_note_id_from_url",
    "parse_note_from_file",
    "CookieManager",
    # 数据模型
    "Note",
    "InterviewQuestion",
]

