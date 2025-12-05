# example_playwright_usage.py
"""
Playwright 版本的小红书笔记提取使用示例
"""
from __future__ import annotations

from xhs_extractor_module.xhs_fetch import fetch_note_from_share_text, fetch_note_from_url
from xhs_extractor_module.xhs_login import login_xhs_and_save_state, check_login_state_exists


def example_1_first_time_login():
    """示例1: 首次登录（只需要运行一次）"""
    print("=" * 60)
    print("示例1: 首次登录")
    print("=" * 60)
    
    # 第一次使用时，需要先登录
    login_xhs_and_save_state()
    
    print("\n✅ 登录完成！下次使用时将自动使用此登录态。")


def example_2_extract_from_share_text():
    """示例2: 从分享文本提取笔记"""
    print("=" * 60)
    print("示例2: 从分享文本提取笔记")
    print("=" * 60)
    
    # 检查是否已登录
    if not check_login_state_exists():
        print("❌ 请先运行登录：python -m xhs_extractor_module.xhs_login")
        return
    
    # 小红书分享文本示例
    share_text = """算法面经：字节大模型Agent 11.16 一面： 请介绍 Tran... http://xhslink.com/o/EEfBYaRn4M 复制后打开【小红书】查看笔记！"""
    
    try:
        # 提取笔记
        note = fetch_note_from_share_text(share_text)
        
        # 打印结果
        print(f"\n标题: {note.title}")
        print(f"正文长度: {len(note.text)} 字符")
        print(f"图片数量: {len(note.images)}")
        print(f"\n正文预览:\n{note.text[:300]}...")
        
        if note.images:
            print(f"\n图片URL（前3张）:")
            for i, img_url in enumerate(note.images[:3], 1):
                print(f"  {i}. {img_url}")
        
        # 可以继续处理，比如：
        # - 调用OCR提取图片文字
        # - 提取面试题
        # - 保存到数据库等
        
    except Exception as e:
        print(f"❌ 错误: {e}")


def example_3_extract_from_url():
    """示例3: 直接从URL提取笔记"""
    print("=" * 60)
    print("示例3: 直接从URL提取笔记")
    print("=" * 60)
    
    if not check_login_state_exists():
        print("❌ 请先运行登录：python -m xhs_extractor_module.xhs_login")
        return
    
    # 可以直接使用URL（短链或完整链接都可以）
    url = "http://xhslink.com/o/EEfBYaRn4M"
    # 或者完整链接: "https://www.xiaohongshu.com/explore/xxxxx"
    
    try:
        note = fetch_note_from_url(url)
        print(f"\n标题: {note.title}")
        print(f"正文: {note.text[:200]}...")
        
    except Exception as e:
        print(f"❌ 错误: {e}")


def example_4_integration_with_existing_pipeline():
    """示例4: 与现有流程集成"""
    print("=" * 60)
    print("示例4: 与现有流程集成")
    print("=" * 60)
    
    if not check_login_state_exists():
        print("❌ 请先运行登录：python -m xhs_extractor_module.xhs_login")
        return
    
    share_text = """算法面经：字节大模型Agent 11.16 一面： 请介绍 Tran... http://xhslink.com/o/EEfBYaRn4M 复制后打开【小红书】查看笔记！"""
    
    try:
        # 1. 提取笔记
        note = fetch_note_from_share_text(share_text)
        
        # 2. 可以继续调用OCR（如果已实现）
        # from ocr import extract_text_from_images
        # note.ocr_text = extract_text_from_images(note.images)
        
        # 3. 可以调用现有的提取面试题功能
        # from extractor import extract_questions_from_note
        # questions = extract_questions_from_note(note)
        
        # 4. 保存或处理
        print(f"\n✅ 笔记提取完成")
        print(f"   标题: {note.title}")
        print(f"   正文: {len(note.text)} 字符")
        print(f"   图片: {len(note.images)} 张")
        print(f"\n   可以继续处理：")
        print(f"   - OCR识别图片文字")
        print(f"   - 提取面试题")
        print(f"   - 保存到数据库")
        
    except Exception as e:
        print(f"❌ 错误: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        if example_num == "1":
            example_1_first_time_login()
        elif example_num == "2":
            example_2_extract_from_share_text()
        elif example_num == "3":
            example_3_extract_from_url()
        elif example_num == "4":
            example_4_integration_with_existing_pipeline()
        else:
            print("用法: python example_playwright_usage.py [1|2|3|4]")
    else:
        print("请选择要运行的示例：")
        print("  1 - 首次登录")
        print("  2 - 从分享文本提取笔记")
        print("  3 - 直接从URL提取笔记")
        print("  4 - 与现有流程集成")
        print("\n用法: python example_playwright_usage.py [1|2|3|4]")

