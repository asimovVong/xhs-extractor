#!/usr/bin/env python3
"""
运行所有测试的脚本
"""
import sys
import unittest
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_all_tests():
    """运行所有测试"""
    # 发现所有测试文件
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent
    suite = loader.discover(
        start_dir=str(start_dir),
        pattern='test_*.py',
        top_level_dir=str(start_dir.parent)
    )
    
    # 运行测试
    runner = unittest.TextTestRunner(
        verbosity=2,
        buffer=True,
    )
    
    print("=" * 60)
    print("运行所有测试")
    print("=" * 60)
    print(f"测试目录: {start_dir}")
    print()
    
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
    
    if result.skipped:
        print(f"\n跳过的测试: {len(result.skipped)} 个")
        print("（通常是因为需要登录态或真实数据）")
    
    # 返回退出码
    return 0 if result.wasSuccessful() else 1


def run_unit_tests_only():
    """只运行单元测试（不需要登录态）"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 只添加单元测试
    from test_xhs_share import TestXhsShare
    from test_xhs_fetch import TestParseNoteFromState, TestFetchNoteMocked
    from test_xhs_login import TestXhsLogin
    
    suite.addTests(loader.loadTestsFromTestCase(TestXhsShare))
    suite.addTests(loader.loadTestsFromTestCase(TestParseNoteFromState))
    suite.addTests(loader.loadTestsFromTestCase(TestFetchNoteMocked))
    suite.addTests(loader.loadTestsFromTestCase(TestXhsLogin))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--unit-only":
        # 只运行单元测试
        sys.exit(run_unit_tests_only())
    else:
        # 运行所有测试
        sys.exit(run_all_tests())

