# test_xhs_login.py
"""
测试 xhs_login 模块
"""
import unittest
import os
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from xhs_extractor_module.xhs_login import (
    login_xhs_and_save_state,
    check_login_state_exists,
    STATE_PATH,
)


class TestXhsLogin(unittest.TestCase):
    """测试登录模块"""
    
    def setUp(self):
        """每个测试前的设置"""
        self.backup_path = None
        if os.path.exists(STATE_PATH):
            self.backup_path = str(STATE_PATH) + ".test_backup"
            os.rename(STATE_PATH, self.backup_path)
    
    def tearDown(self):
        """每个测试后的清理"""
        # 清理测试文件
        if os.path.exists(STATE_PATH):
            os.remove(STATE_PATH)
        
        # 恢复备份文件
        if self.backup_path and os.path.exists(self.backup_path):
            os.rename(self.backup_path, STATE_PATH)
    
    def test_check_login_state_not_exists(self):
        """测试检查不存在的登录态"""
        self.assertFalse(check_login_state_exists())
    
    def test_check_login_state_exists(self):
        """测试检查存在的登录态"""
        # 创建假的登录态文件
        os.makedirs(STATE_PATH.parent, exist_ok=True)
        with open(STATE_PATH, 'w') as f:
            json.dump({"cookies": [], "origins": []}, f)
        
        self.assertTrue(check_login_state_exists())
    
    def test_check_login_state_empty_file(self):
        """测试空文件的情况"""
        os.makedirs(STATE_PATH.parent, exist_ok=True)
        with open(STATE_PATH, 'w') as f:
            f.write("")
        
        self.assertFalse(check_login_state_exists())
    
    @patch('xhs_extractor_module.xhs_login.sync_playwright')
    @patch('builtins.input')
    def test_login_and_save_state_mocked(self, mock_input, mock_playwright):
        """测试登录并保存状态（使用Mock）"""
        # 设置mock
        mock_input.return_value = ""  # 模拟按回车
        
        # Mock Playwright
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()
        
        mock_context.new_page.return_value = mock_page
        mock_browser.new_context.return_value = mock_context
        
        mock_p = MagicMock()
        mock_p.chromium.launch.return_value = mock_browser
        mock_playwright.return_value.__enter__.return_value = mock_p
        
        # 执行登录
        login_xhs_and_save_state()
        
        # 验证
        mock_p.chromium.launch.assert_called_once_with(headless=False, slow_mo=100)
        mock_page.goto.assert_called_once_with(
            "https://www.xiaohongshu.com",
            wait_until="networkidle"
        )
        mock_context.storage_state.assert_called_once()
        mock_browser.close.assert_called_once()
        
        # 验证文件是否创建
        self.assertTrue(os.path.exists(STATE_PATH))


if __name__ == "__main__":
    unittest.main()

