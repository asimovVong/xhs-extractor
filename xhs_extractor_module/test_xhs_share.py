# test_xhs_share.py
"""
测试 xhs_share 模块
"""
import unittest
from xhs_extractor_module.xhs_share import extract_xhs_url_from_share_text


class TestXhsShare(unittest.TestCase):
    """测试分享文本URL提取"""
    
    def test_extract_standard_share_text(self):
        """测试标准分享文本格式"""
        text = "算法面经：字节大模型Agent 11.16 一面： 请介绍 Tran... http://xhslink.com/o/EEfBYaRn4M 复制后打开【小红书】查看笔记！"
        url = extract_xhs_url_from_share_text(text)
        self.assertEqual(url, "http://xhslink.com/o/EEfBYaRn4M")
    
    def test_extract_https_link(self):
        """测试https链接"""
        text = "笔记内容 https://xhslink.com/o/ABC123 复制后打开"
        url = extract_xhs_url_from_share_text(text)
        self.assertEqual(url, "https://xhslink.com/o/ABC123")
    
    def test_extract_with_punctuation(self):
        """测试带标点符号的链接"""
        text = "内容 http://xhslink.com/o/XYZ789，复制后打开。"
        url = extract_xhs_url_from_share_text(text)
        self.assertEqual(url, "http://xhslink.com/o/XYZ789")
    
    def test_extract_with_chinese_punctuation(self):
        """测试中文标点符号"""
        text = "内容 http://xhslink.com/o/DEF456）复制后打开"
        url = extract_xhs_url_from_share_text(text)
        self.assertEqual(url, "http://xhslink.com/o/DEF456")
    
    def test_extract_full_url(self):
        """测试完整的小红书链接"""
        text = "笔记 https://www.xiaohongshu.com/explore/abc123def456 查看"
        url = extract_xhs_url_from_share_text(text)
        self.assertTrue(url.startswith("https://www.xiaohongshu.com"))
    
    def test_no_url_found(self):
        """测试没有URL的情况"""
        text = "这是一段没有链接的文本"
        url = extract_xhs_url_from_share_text(text)
        self.assertIsNone(url)
    
    def test_empty_text(self):
        """测试空文本"""
        url = extract_xhs_url_from_share_text("")
        self.assertIsNone(url)
    
    def test_none_text(self):
        """测试None输入"""
        url = extract_xhs_url_from_share_text(None)
        self.assertIsNone(url)
    
    def test_multiple_urls(self):
        """测试多个URL的情况（应该返回第一个）"""
        text = "第一个链接 http://xhslink.com/o/FIRST 第二个链接 http://xhslink.com/o/SECOND"
        url = extract_xhs_url_from_share_text(text)
        self.assertEqual(url, "http://xhslink.com/o/FIRST")


if __name__ == "__main__":
    unittest.main()

