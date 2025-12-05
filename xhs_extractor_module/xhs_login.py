# xhs_login.py
"""
小红书登录模块
使用 Playwright 进行网页登录并保存登录态
"""
from __future__ import annotations

import os
from pathlib import Path
from playwright.sync_api import sync_playwright


# 登录态文件路径（保存在模块目录下）
STATE_PATH = Path(__file__).parent / "xhs_state.json"


def login_xhs_and_save_state(state_path: str = None):
    """
    第一次运行时调用：
    - 打开带 UI 的 Chromium
    - 访问小红书官网
    - 用户手工扫码 / 输入手机号登录
    - 登录完后在终端按回车，脚本会把当前登录态写入 xhs_state.json
    
    Args:
        state_path: 登录态保存路径，默认为模块目录下的 xhs_state.json
    """
    if state_path is None:
        state_path = str(STATE_PATH)
    
    print("=" * 60)
    print("小红书登录助手")
    print("=" * 60)
    print(f"登录态将保存到: {state_path}")
    print("\n正在打开浏览器...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=100)
        context = browser.new_context()
        page = context.new_page()
        
        print("\n正在访问小红书官网...")
        page.goto("https://www.xiaohongshu.com", wait_until="networkidle")
        
        print("\n" + "=" * 60)
        print("请在打开的浏览器里完成小红书登录：")
        print("  - 可以使用手机号登录")
        print("  - 也可以使用扫码登录")
        print("  - 登录成功后，回到终端按回车继续...")
        print("=" * 60)
        
        input("\n登录完成后按回车：")
        
        # 持久化当前 context 的 cookie / localStorage 等
        context.storage_state(path=state_path)
        
        print(f"\n✅ 登录状态已保存到: {state_path}")
        print("下次使用时将自动使用此登录态，无需再次登录。")
        
        browser.close()


def check_login_state_exists(state_path: str = None) -> bool:
    """
    检查登录态文件是否存在
    
    Args:
        state_path: 登录态文件路径，默认为模块目录下的 xhs_state.json
    
    Returns:
        如果文件存在返回True，否则返回False
    """
    if state_path is None:
        state_path = str(STATE_PATH)
    
    return os.path.exists(state_path) and os.path.getsize(state_path) > 0


if __name__ == "__main__":
    login_xhs_and_save_state()

