#!/usr/bin/env python3
"""
小红书笔记提取模块 - 完整使用示例
"""
from xhs_extractor_module.xhs_parser import fetch_xhs_note, extract_note_id_from_url
from xhs_extractor_module.ocr import OCRProcessor, extract_ocr_from_note
from xhs_extractor_module.cookie_manager import CookieManager
from xhs_extractor_module.models import Note


def example_1_simple_extraction():
    """示例1: 最简单的提取（无 Cookie）"""
    print("=" * 50)
    print("示例1: 简单提取（可能需要登录）")
    print("=" * 50)
    
    url = "https://www.xiaohongshu.com/explore/xxxxx"
    
    try:
        note = fetch_xhs_note(url)
        print(f"标题: {note.title}")
        print(f"文本长度: {len(note.text)} 字符")
        print(f"图片数量: {len(note.images)}")
        print(f"\n文本预览:\n{note.text[:200]}...")
    except ValueError as e:
        print(f"提取失败: {e}")
        print("提示: 可能需要 Cookie 才能访问")


def example_2_with_cookie():
    """示例2: 使用 Cookie 提取"""
    print("\n" + "=" * 50)
    print("示例2: 使用 Cookie 提取")
    print("=" * 50)
    
    url = "https://www.xiaohongshu.com/explore/xxxxx"
    cookie_manager = CookieManager()
    
    # 方式1: 使用已保存的 Cookie
    saved_cookies = cookie_manager.load_saved_cookies()
    if saved_cookies:
        cookie_string = cookie_manager.cookie_dict_to_string(saved_cookies)
        print("使用已保存的 Cookie")
        note = fetch_xhs_note(url, cookie_string=cookie_string)
    else:
        print("没有已保存的 Cookie，需要手动提供")
        # 方式2: 使用新 Cookie
        cookie_str = input("请输入 Cookie 字符串（从浏览器 Network 面板复制）: ")
        cookies_dict = cookie_manager.parse_cookie_string(cookie_str)
        cookie_manager.save_cookies(cookies_dict)
        note = fetch_xhs_note(url, cookie_string=cookie_str)
    
    print(f"标题: {note.title}")
    print(f"文本: {note.text[:200]}...")


def example_3_with_ocr():
    """示例3: 完整流程（包含 OCR）"""
    print("\n" + "=" * 50)
    print("示例3: 完整流程（包含 OCR）")
    print("=" * 50)
    
    url = "https://www.xiaohongshu.com/explore/xxxxx"
    cookie_manager = CookieManager()
    
    # 1. 获取笔记
    saved_cookies = cookie_manager.load_saved_cookies()
    cookie_string = None
    if saved_cookies:
        cookie_string = cookie_manager.cookie_dict_to_string(saved_cookies)
    
    note = fetch_xhs_note(url, cookie_string=cookie_string)
    print(f"✓ 获取笔记成功: {note.title}")
    print(f"  - 文本长度: {len(note.text)} 字符")
    print(f"  - 图片数量: {len(note.images)}")
    
    # 2. OCR 处理
    if note.images:
        print(f"\n开始 OCR 处理 {len(note.images)} 张图片...")
        ocr_processor = OCRProcessor()
        note.ocr_text = extract_ocr_from_note(note, ocr_processor)
        print(f"✓ OCR 完成，识别文字: {len(note.ocr_text)} 字符")
    else:
        print("没有图片，跳过 OCR")
    
    # 3. 合并文本
    full_text = note.text
    if note.ocr_text:
        full_text += "\n\n[图片 OCR 文本]\n" + note.ocr_text
    
    print(f"\n完整文本总长度: {len(full_text)} 字符")
    print(f"\n完整文本预览:\n{full_text[:500]}...")


def example_4_cookie_management():
    """示例4: Cookie 管理"""
    print("\n" + "=" * 50)
    print("示例4: Cookie 管理")
    print("=" * 50)
    
    cookie_manager = CookieManager()
    
    # 1. 解析 Cookie 字符串
    cookie_str = "a1=19ae9e8b405bvmc17fsbo3...; web_session=xxx; webId=yyy; xsecappid=xhs-pc-web"
    cookies_dict = cookie_manager.parse_cookie_string(cookie_str)
    print(f"解析 Cookie: {len(cookies_dict)} 个")
    print(f"  Cookie 键: {list(cookies_dict.keys())}")
    
    # 2. 保存 Cookie
    cookie_manager.save_cookies(cookies_dict)
    print("✓ Cookie 已保存")
    
    # 3. 加载 Cookie
    loaded_cookies = cookie_manager.load_saved_cookies()
    print(f"✓ Cookie 已加载: {len(loaded_cookies) if loaded_cookies else 0} 个")
    
    # 4. 转换为字符串
    if loaded_cookies:
        cookie_string = cookie_manager.cookie_dict_to_string(loaded_cookies)
        print(f"Cookie 字符串长度: {len(cookie_string)} 字符")


def example_5_error_handling():
    """示例5: 错误处理"""
    print("\n" + "=" * 50)
    print("示例5: 错误处理")
    print("=" * 50)
    
    url = "https://www.xiaohongshu.com/explore/xxxxx"
    
    try:
        note = fetch_xhs_note(url)
        # 处理成功的情况
        print(f"✓ 提取成功: {note.title}")
        
    except ValueError as e:
        error_msg = str(e)
        
        if "需要 Cookie" in error_msg or "登录" in error_msg:
            print("⚠ 需要登录 Cookie")
            print("解决方案:")
            print("  1. 在浏览器中打开链接并登录")
            print("  2. 从 Network 面板复制 Cookie")
            print("  3. 使用 Cookie 重新提取")
        else:
            print(f"✗ 提取失败: {error_msg}")
    
    except Exception as e:
        print(f"✗ 未知错误: {e}")
        import traceback
        traceback.print_exc()


def example_6_batch_processing():
    """示例6: 批量处理"""
    print("\n" + "=" * 50)
    print("示例6: 批量处理多个链接")
    print("=" * 50)
    
    urls = [
        "https://www.xiaohongshu.com/explore/xxxxx1",
        "https://www.xiaohongshu.com/explore/xxxxx2",
        "https://www.xiaohongshu.com/explore/xxxxx3",
    ]
    
    cookie_manager = CookieManager()
    saved_cookies = cookie_manager.load_saved_cookies()
    cookie_string = None
    if saved_cookies:
        cookie_string = cookie_manager.cookie_dict_to_string(saved_cookies)
    
    notes = []
    for i, url in enumerate(urls, 1):
        print(f"\n处理链接 {i}/{len(urls)}: {url}")
        try:
            note = fetch_xhs_note(url, cookie_string=cookie_string)
            notes.append(note)
            print(f"  ✓ 成功: {note.title}")
        except Exception as e:
            print(f"  ✗ 失败: {e}")
    
    print(f"\n批量处理完成: {len(notes)}/{len(urls)} 成功")


if __name__ == "__main__":
    print("小红书笔记提取模块 - 使用示例\n")
    
    # 运行示例（根据实际情况取消注释）
    # example_1_simple_extraction()
    # example_2_with_cookie()
    # example_3_with_ocr()
    # example_4_cookie_management()
    # example_5_error_handling()
    # example_6_batch_processing()
    
    print("\n提示: 取消注释上面的函数调用来运行相应示例")

