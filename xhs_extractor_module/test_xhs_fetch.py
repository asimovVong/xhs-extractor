# test_xhs_fetch.py
"""
测试 xhs_fetch 模块
需要先运行登录脚本生成 xhs_state.json
"""
import unittest
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from xhs_extractor_module.xhs_fetch import (
    fetch_note_from_share_text,
    fetch_note_from_url,
    _parse_note_from_state,
)
from xhs_extractor_module.models import Note
from xhs_extractor_module.xhs_login import STATE_PATH


class TestParseNoteFromState(unittest.TestCase):
    """测试从state解析Note"""
    
    def test_parse_structure_1(self):
        """测试结构1: state['note']['noteDetailMap'][firstNoteId]['note']"""
        state = {
            "note": {
                "firstNoteId": "note123",
                "noteDetailMap": {
                    "note123": {
                        "note": {
                            "noteId": "note123",
                            "title": "测试标题",
                            "desc": "测试正文内容",
                            "imageList": [
                                {"url": "https://example.com/img1.jpg"},
                                {"url": "https://example.com/img2.jpg"},
                            ]
                        }
                    }
                }
            }
        }
        
        note = _parse_note_from_state(state, "https://www.xiaohongshu.com/explore/note123")
        
        self.assertEqual(note.id, "note123")
        self.assertEqual(note.title, "测试标题")
        self.assertEqual(note.text, "测试正文内容")
        self.assertEqual(len(note.images), 2)
        self.assertIn("https://example.com/img1.jpg", note.images)
    
    def test_parse_structure_2(self):
        """测试结构2: state['noteData']['data']['noteData']"""
        state = {
            "noteData": {
                "data": {
                    "noteData": {
                        "noteId": "note456",
                        "displayTitle": "显示标题",
                        "noteContent": "笔记内容",
                        "images": [
                            {"originUrl": "https://example.com/img3.jpg"},
                        ]
                    }
                }
            }
        }
        
        note = _parse_note_from_state(state, "https://www.xiaohongshu.com/explore/note456")
        
        self.assertEqual(note.id, "note456")
        self.assertEqual(note.title, "显示标题")
        self.assertEqual(note.text, "笔记内容")
        self.assertEqual(len(note.images), 1)
    
    def test_parse_missing_data(self):
        """测试缺少数据的情况"""
        state = {
            "other": "data"
        }
        
        note = _parse_note_from_state(state, "https://www.xiaohongshu.com/explore/abc123")
        
        # 应该返回一个基础的Note对象，而不是抛出异常
        self.assertIsInstance(note, Note)
        self.assertEqual(note.title, "未找到标题")
        self.assertEqual(note.text, "")
    
    def test_parse_various_image_fields(self):
        """测试各种图片字段名"""
        state = {
            "note": {
                "firstNoteId": "note789",
                "noteDetailMap": {
                    "note789": {
                        "note": {
                            "noteId": "note789",
                            "title": "测试",
                            "desc": "内容",
                            "imageInfoList": [
                                {"urlDefault": "https://example.com/img4.jpg"},
                                {"picUrl": "https://example.com/img5.jpg"},
                                {"info": {"url": "https://example.com/img6.jpg"}},
                            ]
                        }
                    }
                }
            }
        }
        
        note = _parse_note_from_state(state, "https://www.xiaohongshu.com/explore/note789")
        
        self.assertEqual(len(note.images), 3)
        self.assertIn("https://example.com/img4.jpg", note.images)
        self.assertIn("https://example.com/img5.jpg", note.images)
        self.assertIn("https://example.com/img6.jpg", note.images)


class TestFetchNoteIntegration(unittest.TestCase):
    """集成测试（需要真实的登录态）"""
    
    @classmethod
    def setUpClass(cls):
        """检查登录态文件是否存在"""
        cls.has_login_state = os.path.exists(STATE_PATH) and os.path.getsize(STATE_PATH) > 0
        if not cls.has_login_state:
            print("\n⚠ 警告: 未找到登录态文件，跳过集成测试")
            print(f"   请先运行: python -m xhs_extractor_module.xhs_login")
    
    def test_fetch_note_no_login_state(self):
        """测试没有登录态的情况"""
        if self.has_login_state:
            self.skipTest("已有登录态，跳过此测试")
        
        # 临时重命名登录态文件
        backup_path = str(STATE_PATH) + ".backup"
        if os.path.exists(STATE_PATH):
            os.rename(STATE_PATH, backup_path)
        
        try:
            with self.assertRaises(ValueError) as context:
                fetch_note_from_share_text("测试 http://xhslink.com/o/TEST 复制后打开")
            
            self.assertIn("登录态文件不存在", str(context.exception))
        finally:
            # 恢复登录态文件
            if os.path.exists(backup_path):
                os.rename(backup_path, STATE_PATH)
    
    @unittest.skipUnless(
        os.path.exists(STATE_PATH) and os.path.getsize(STATE_PATH) > 0,
        "需要先运行登录脚本"
    )
    def test_fetch_note_with_mock_url(self):
        """测试使用模拟URL（不实际访问网络）"""
        # 这个测试需要mock Playwright，比较复杂
        # 实际使用时应该用真实的分享文本测试
        pass


class TestFetchNoteMocked(unittest.TestCase):
    """使用Mock的单元测试"""
    
    @patch('xhs_extractor_module.xhs_fetch.sync_playwright')
    @patch('xhs_extractor_module.xhs_fetch.check_login_state_exists')
    def test_fetch_note_mocked(self, mock_check_login, mock_playwright):
        """测试使用Mock的fetch_note"""
        # 设置mock
        mock_check_login.return_value = True
        
        # Mock Playwright
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()
        
        mock_page.url = "https://www.xiaohongshu.com/explore/abc123"
        mock_page.evaluate.return_value = {
            "note": {
                "firstNoteId": "abc123",
                "noteDetailMap": {
                    "abc123": {
                        "note": {
                            "noteId": "abc123",
                            "title": "Mock标题",
                            "desc": "Mock正文",
                            "imageList": []
                        }
                    }
                }
            }
        }
        
        mock_context.new_page.return_value = mock_page
        mock_browser.new_context.return_value = mock_context
        
        mock_p = MagicMock()
        mock_p.chromium.launch.return_value = mock_browser
        mock_playwright.return_value.__enter__.return_value = mock_p
        
        # 测试
        share_text = "测试 http://xhslink.com/o/TEST 复制后打开"
        note = fetch_note_from_share_text(share_text)
        
        # 验证
        self.assertEqual(note.title, "Mock标题")
        self.assertEqual(note.text, "Mock正文")
        mock_browser.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()

