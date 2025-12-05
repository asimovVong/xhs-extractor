# test_integration.py
"""
集成测试 - 需要真实的登录态和网络连接
运行前请确保：
1. 已运行登录脚本生成 xhs_state.json
2. 有网络连接
3. 准备一个真实的小红书分享文本用于测试
"""
import unittest
import os
from xhs_extractor_module.xhs_fetch import fetch_note_from_share_text, fetch_note_from_url
from xhs_extractor_module.xhs_share import extract_xhs_url_from_share_text
from xhs_extractor_module.xhs_login import check_login_state_exists, STATE_PATH


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    @classmethod
    def setUpClass(cls):
        """检查前置条件"""
        cls.has_login_state = check_login_state_exists()
        if not cls.has_login_state:
            print("\n⚠ 警告: 未找到登录态文件")
            print(f"   请先运行: python -m xhs_extractor_module.xhs_login")
    
    def setUp(self):
        """每个测试前的检查"""
        if not self.has_login_state:
            self.skipTest("需要先运行登录脚本")
    
    @unittest.skip("需要真实的小红书分享文本")
    def test_extract_real_share_text(self):
        """测试真实的分享文本提取"""
        # 替换为真实的小红书分享文本
        share_text = """算法面经：字节大模型Agent 11.16 一面： 请介绍 Tran... http://xhslink.com/o/EEfBYaRn4M 复制后打开【小红书】查看笔记！"""
        
        # 提取URL
        url = extract_xhs_url_from_share_text(share_text)
        self.assertIsNotNone(url)
        self.assertTrue(url.startswith("http"))
        
        # 提取笔记
        note = fetch_note_from_share_text(share_text)
        
        # 验证结果
        self.assertIsNotNone(note)
        self.assertIsNotNone(note.id)
        self.assertIsNotNone(note.url)
        self.assertIsNotNone(note.title)
        # 正文可能为空（某些笔记只有图片）
        # self.assertTrue(len(note.text) > 0 or len(note.images) > 0)
        
        print(f"\n✅ 提取成功:")
        print(f"   标题: {note.title}")
        print(f"   正文长度: {len(note.text)} 字符")
        print(f"   图片数量: {len(note.images)}")
        if note.images:
            print(f"   第一张图片: {note.images[0]}")
    
    @unittest.skip("需要真实的小红书URL")
    def test_fetch_from_real_url(self):
        """测试从真实URL提取"""
        # 替换为真实的小红书URL
        url = "http://xhslink.com/o/EEfBYaRn4M"
        
        note = fetch_note_from_url(url)
        
        self.assertIsNotNone(note)
        self.assertIsNotNone(note.id)
        self.assertTrue(note.url.startswith("https://www.xiaohongshu.com"))
        
        print(f"\n✅ 从URL提取成功:")
        print(f"   标题: {note.title}")
        print(f"   URL: {note.url}")
    
    def test_error_handling_invalid_share_text(self):
        """测试无效分享文本的错误处理"""
        with self.assertRaises(ValueError) as context:
            fetch_note_from_share_text("这是一段没有链接的文本")
        
        self.assertIn("没有找到", str(context.exception))
    
    def test_error_handling_empty_text(self):
        """测试空文本的错误处理"""
        with self.assertRaises(ValueError) as context:
            fetch_note_from_share_text("")
        
        self.assertIn("没有找到", str(context.exception))


class TestEndToEnd(unittest.TestCase):
    """端到端测试"""
    
    @classmethod
    def setUpClass(cls):
        """检查前置条件"""
        cls.has_login_state = check_login_state_exists()
        if not cls.has_login_state:
            print("\n⚠ 警告: 未找到登录态文件，跳过端到端测试")
    
    @unittest.skip("需要真实数据")
    def test_full_workflow(self):
        """测试完整工作流程"""
        # 1. 分享文本
        share_text = """算法面经：字节大模型Agent 11.16 一面： 请介绍 Tran... http://xhslink.com/o/EEfBYaRn4M 复制后打开【小红书】查看笔记！"""
        
        # 2. 提取笔记
        note = fetch_note_from_share_text(share_text)
        
        # 3. 验证数据完整性
        self.assertIsNotNone(note.id)
        self.assertIsNotNone(note.url)
        self.assertIsNotNone(note.title)
        
        # 4. 验证可以继续处理
        # 例如：OCR、提取面试题等
        full_text = note.text
        if note.ocr_text:
            full_text += "\n\n" + note.ocr_text
        
        self.assertIsInstance(full_text, str)
        
        print(f"\n✅ 完整流程测试通过")
        print(f"   笔记ID: {note.id}")
        print(f"   标题: {note.title}")
        print(f"   完整文本长度: {len(full_text)} 字符")


if __name__ == "__main__":
    # 运行测试
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有测试
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEnd))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 打印总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"运行: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"跳过: {len(result.skipped)}")
    
    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"  - {test}")

