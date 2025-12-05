# xhs_fetch.py
"""
小红书笔记抓取模块
使用 Playwright 和已保存的登录态抓取笔记内容
"""
from __future__ import annotations

import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

from .xhs_share import extract_xhs_url_from_share_text
from .models import Note
from .xhs_login import STATE_PATH, check_login_state_exists


def _parse_note_from_state(state: Dict[str, Any], url: str) -> Note:
    """
    从 window.__INITIAL_STATE__ 的 Python dict 中，解析出 Note 对象。
    
    这里实现了多种常见结构的解析，以兼容小红书可能的不同数据结构。
    
    Args:
        state: window.__INITIAL_STATE__ 的字典对象
        url: 笔记的最终URL
    
    Returns:
        Note 对象
    
    Raises:
        RuntimeError: 如果无法从state中找到笔记数据结构
    """
    note_data = None
    note_id = None
    
    # 结构 1: state['note']['noteDetailMap'][firstNoteId]['note']
    if "note" in state and isinstance(state["note"], dict):
        note_root = state["note"]
        first_id = note_root.get("firstNoteId")
        detail_map = note_root.get("noteDetailMap")
        
        # 确保 first_id 是字符串或可哈希类型
        if first_id and detail_map:
            # 处理 detail_map 是字典的情况
            if isinstance(detail_map, dict):
                # 如果 first_id 是字典，尝试转换为字符串
                if isinstance(first_id, dict):
                    # 尝试从字典中提取ID
                    first_id = first_id.get("id") or first_id.get("noteId") or str(first_id)
                elif not isinstance(first_id, (str, int)):
                    first_id = str(first_id)
                
                # 确保 first_id 是可哈希的
                try:
                    inner = detail_map.get(first_id, {})
                    if isinstance(inner, dict):
                        note_data = inner.get("note", inner)
                        note_id = str(first_id)
                except (TypeError, AttributeError) as e:
                    # 如果 detail_map 不是字典，或者 first_id 不可哈希，跳过这个结构
                    print(f"⚠ 警告：解析结构1时出错: {e}")
                    print(f"   first_id 类型: {type(first_id)}, 值: {first_id}")
                    print(f"   detail_map 类型: {type(detail_map)}")
                    pass
            
            # 处理 detail_map 是列表的情况
            elif isinstance(detail_map, list) and len(detail_map) > 0:
                # 如果 detail_map 是列表，取第一个元素
                first_item = detail_map[0]
                if isinstance(first_item, dict):
                    note_data = first_item.get("note", first_item)
                    note_id = first_item.get("id") or first_item.get("noteId") or str(first_id) if first_id else None
    
    # 结构 2: state['noteData']['data']['noteData']
    if note_data is None and "noteData" in state:
        nd = state["noteData"]
        if isinstance(nd, dict):
            if "data" in nd and isinstance(nd["data"], dict) and "noteData" in nd["data"]:
                note_data = nd["data"]["noteData"]
            else:
                note_data = nd
    
    # 结构 3: state['noteDetail']
    if note_data is None and "noteDetail" in state:
        note_data = state["noteDetail"]
    
    # 结构 4: 尝试从其他可能的路径查找
    if note_data is None:
        for key in list(state.keys()):  # 使用list()避免在迭代时修改字典
            if 'note' in key.lower() and isinstance(state[key], dict):
                # 尝试查找嵌套的note数据
                try:
                    if "note" in state[key]:
                        note_data = state[key]["note"]
                        break
                    elif "data" in state[key] and isinstance(state[key]["data"], dict):
                        if "note" in state[key]["data"]:
                            note_data = state[key]["data"]["note"]
                            break
                        elif "noteData" in state[key]["data"]:
                            note_data = state[key]["data"]["noteData"]
                            break
                except (TypeError, AttributeError, KeyError):
                    continue
    
    if note_data is None:
        # 打印state的keys帮助调试
        print("⚠ 警告：未能在 __INITIAL_STATE__ 中找到 note 数据结构")
        print(f"   state 的 keys: {list(state.keys())[:20]}")  # 只显示前20个
        
        # 尝试深度搜索所有可能包含note数据的路径
        def find_note_data(obj, path="", max_depth=3):
            """递归查找包含note数据的对象"""
            if max_depth <= 0:
                return None
            if not isinstance(obj, dict):
                return None
            
            # 检查当前对象是否包含note相关字段
            for key in ['note', 'noteData', 'noteDetail', 'noteCard']:
                if key in obj:
                    val = obj[key]
                    # 处理Vue响应式对象
                    if isinstance(val, dict) and ('_value' in val or '_rawValue' in val):
                        val = val.get('_value') or val.get('_rawValue')
                    if isinstance(val, dict) and (val.get('title') or val.get('desc') or val.get('noteId')):
                        return val
            
            # 递归搜索
            for key, value in obj.items():
                if key.startswith('__') or key in ['dep', '__v_isRef']:
                    continue
                if isinstance(value, dict):
                    result = find_note_data(value, f"{path}.{key}", max_depth - 1)
                    if result:
                        return result
                elif isinstance(value, list) and len(value) > 0:
                    for i, item in enumerate(value[:5]):  # 只检查前5个元素
                        if isinstance(item, dict):
                            result = find_note_data(item, f"{path}.{key}[{i}]", max_depth - 1)
                            if result:
                                return result
            return None
        
        # 尝试深度搜索
        note_data = find_note_data(state)
        
        if note_data:
            print(f"   ✅ 通过深度搜索找到笔记数据")
        else:
            print("   尝试从URL提取基本信息...")
        
        # 尝试从URL提取note_id
        import re
        patterns = [
            r'/explore/([a-f0-9]+)',
            r'/discovery/item/([a-f0-9]+)',
            r'/user/[^/]+/([a-f0-9]+)',
        ]
        note_id_match = None
        for pattern in patterns:
            note_id_match = re.search(pattern, url)
            if note_id_match:
                break
        
        if note_id_match:
            note_id = note_id_match.group(1)
        else:
            import uuid
            note_id = str(uuid.uuid4())
        
        # 返回一个基础的Note对象
        return Note(
            id=str(note_id),
            url=url,
            title="未找到标题",
            text="",
            images=[],
            ocr_text="",
            raw={"state_keys": list(state.keys()), "error": "无法解析note数据"},
        )
    
    # 辅助函数：提取Vue响应式对象的实际值
    def extract_vue_value(obj):
        """提取Vue响应式对象的实际值"""
        if obj is None:
            return None
        if isinstance(obj, dict):
            # 检查是否是Vue响应式对象
            if '_value' in obj:
                return extract_vue_value(obj['_value'])
            elif '_rawValue' in obj:
                return extract_vue_value(obj['_rawValue'])
            # 如果对象只有一个'value'键，可能是包装对象
            elif 'value' in obj and len([k for k in obj.keys() if not k.startswith('__')]) == 1:
                return extract_vue_value(obj['value'])
        return obj
    
    # 提取标题（处理Vue响应式对象）
    title = (
        extract_vue_value(note_data.get("title"))
        or extract_vue_value(note_data.get("displayTitle"))
        or extract_vue_value(note_data.get("noteCard", {}).get("displayTitle", ""))
        or ""
    )
    if isinstance(title, dict):
        title = extract_vue_value(title) or ""
    title = str(title) if title else ""
    
    # 提取正文（处理Vue响应式对象）
    text = (
        extract_vue_value(note_data.get("desc"))
        or extract_vue_value(note_data.get("noteContent"))
        or extract_vue_value(note_data.get("content"))
        or extract_vue_value(note_data.get("text"))
        or ""
    )
    if isinstance(text, dict):
        text = extract_vue_value(text) or ""
    text = str(text) if text else ""
    
    # 提取note_id
    if not note_id:
        note_id = (
            extract_vue_value(note_data.get("noteId"))
            or extract_vue_value(note_data.get("id"))
            or extract_vue_value(note_data.get("note_id"))
        )
    
    # 处理Vue响应式对象（如果note_id是字典且包含_value或_rawValue）
    if isinstance(note_id, dict):
        note_id = extract_vue_value(note_id)
    
    # 如果还是没有note_id，尝试从URL提取
    if not note_id:
        import re
        # 尝试多种URL格式
        note_id_match = (
            re.search(r'/explore/([a-f0-9]+)', url) or
            re.search(r'/discovery/item/([a-f0-9]+)', url) or
            re.search(r'/user/[^/]+/([a-f0-9]+)', url)
        )
        if note_id_match:
            note_id = note_id_match.group(1)
        else:
            import uuid
            note_id = str(uuid.uuid4())
    
    # 确保note_id是字符串（使用extract_vue_value处理Vue响应式对象）
    if note_id and isinstance(note_id, dict):
        note_id = extract_vue_value(note_id)
    note_id = str(note_id) if note_id else str(uuid.uuid4())
    
    # 提取图片列表
    images: List[str] = []
    image_keys = ["imageList", "imageInfoList", "images", "image_list"]
    
    for key in image_keys:
        imgs = note_data.get(key)
        # 处理Vue响应式对象
        imgs = extract_vue_value(imgs) if imgs else None
        
        if isinstance(imgs, list) and imgs:
            for img in imgs:
                # 处理Vue响应式对象
                img = extract_vue_value(img) if isinstance(img, dict) else img
                
                if not isinstance(img, dict):
                    if isinstance(img, str) and img.startswith("http"):
                        images.append(img)
                    continue
                
                # 尝试多种可能的图片URL字段
                url_field = None
                url_keys = ["url", "originUrl", "original", "imgUrl", "urlDefault", "picUrl"]
                
                for kk in url_keys:
                    v = extract_vue_value(img.get(kk))
                    if isinstance(v, str) and v.startswith("http"):
                        url_field = v
                        break
                
                # 如果直接字段没有，尝试嵌套结构
                if not url_field:
                    for nested_key in ["info", "imageInfo"]:
                        nested = extract_vue_value(img.get(nested_key))
                        if isinstance(nested, dict):
                            for kk in url_keys:
                                v = extract_vue_value(nested.get(kk))
                                if isinstance(v, str) and v.startswith("http"):
                                    url_field = v
                                    break
                            if url_field:
                                break
                
                if url_field and url_field not in images:  # 去重
                    images.append(url_field)
            
            if images:  # 如果找到了图片，就不再尝试其他key
                break
    
    return Note(
        id=str(note_id),
        url=url,
        title=title or "未命名笔记",
        text=text,
        images=images,
        ocr_text="",  # 后面可以再接 OCR
        raw=note_data,
    )


def fetch_note_from_share_text(share_text: str, state_path: str = None) -> Note:
    """
    高层接口：
    - 输入：小红书分享文本（包含 xhslink 短链）
    - 输出：解析好的 Note（标题、正文、图片 URL）
    
    Args:
        share_text: 小红书分享文本，例如：
            "算法面经：字节大模型Agent 11.16 一面： 请介绍 Tran... http://xhslink.com/o/EEfBYaRn4M 复制后打开【小红书】查看笔记！"
        state_path: 登录态文件路径，默认为模块目录下的 xhs_state.json
    
    Returns:
        Note 对象，包含解析出的笔记内容
    
    Raises:
        ValueError: 如果分享文本中没有找到链接，或登录态文件不存在
        RuntimeError: 如果无法获取页面或解析内容
    """
    if state_path is None:
        state_path = str(STATE_PATH)
    
    # 检查登录态文件是否存在
    if not check_login_state_exists(state_path):
        raise ValueError(
            f"登录态文件不存在: {state_path}\n"
            "请先运行以下命令进行登录：\n"
            f"  python -m xhs_extractor_module.xhs_login"
        )
    
    # 提取短链
    short_url = extract_xhs_url_from_share_text(share_text)
    if not short_url:
        raise ValueError("分享文本中没有找到小红书链接")
    
    print(f"提取到链接: {short_url}")
    print("正在使用 Playwright 访问页面...")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(storage_state=state_path)
            page = context.new_page()
            
            # 直接打开短链，Playwright 会自动跟踪到 explore 的真实链接
            try:
                page.goto(short_url, wait_until="networkidle", timeout=30000)
            except PlaywrightTimeoutError:
                # 如果networkidle超时，尝试domcontentloaded
                page.goto(short_url, wait_until="domcontentloaded", timeout=30000)
            
            final_url = page.url
            print(f"最终URL: {final_url}")
            
            # 等待页面加载完成，确保 __INITIAL_STATE__ 已设置
            try:
                page.wait_for_function(
                    "() => window.__INITIAL_STATE__ !== undefined",
                    timeout=10000
                )
            except PlaywrightTimeoutError:
                print("⚠ 警告：等待 __INITIAL_STATE__ 超时，尝试直接获取...")
            
            # 在浏览器里序列化 __INITIAL_STATE__ 对象
            # 使用 JSON.stringify 避免序列化错误（循环引用或对象过大）
            try:
                state_json = page.evaluate("""
                    () => {
                        // 递归函数：提取Vue响应式对象的值
                        function extractVueValue(obj, seen = new WeakSet()) {
                            if (obj === null || obj === undefined) return null;
                            
                            // 防止循环引用
                            if (typeof obj === 'object' && obj !== null) {
                                if (seen.has(obj)) {
                                    return '[Circular]';
                                }
                                seen.add(obj);
                            }
                            
                            // 如果是Vue响应式对象，提取_value或_rawValue
                            if (obj && typeof obj === 'object' && ('_value' in obj || '_rawValue' in obj)) {
                                return extractVueValue(obj._value || obj._rawValue, seen);
                            }
                            
                            // 如果是数组，递归处理每个元素
                            if (Array.isArray(obj)) {
                                return obj.map(item => extractVueValue(item, seen));
                            }
                            
                            // 如果是对象，递归处理每个属性
                            if (typeof obj === 'object' && obj !== null) {
                                const result = {};
                                for (const key in obj) {
                                    // 跳过Vue内部属性
                                    if (key.startsWith('__v_') || key === 'dep') continue;
                                    try {
                                        result[key] = extractVueValue(obj[key], seen);
                                    } catch (e) {
                                        // 如果提取失败，跳过这个属性
                                        continue;
                                    }
                                }
                                return result;
                            }
                            
                            return obj;
                        }
                        
                        try {
                            // 先提取Vue响应式对象的值，再序列化
                            const extracted = extractVueValue(window.__INITIAL_STATE__);
                            return JSON.stringify(extracted);
                        } catch (e) {
                            // 如果失败，尝试处理循环引用
                            const seen = new WeakSet();
                            return JSON.stringify(window.__INITIAL_STATE__, (key, val) => {
                                if (val != null && typeof val === "object") {
                                    if (seen.has(val)) {
                                        return "[Circular]";
                                    }
                                    seen.add(val);
                                }
                                return val;
                            });
                        }
                    }
                """)
                
                if not state_json:
                    raise RuntimeError("无法获取 window.__INITIAL_STATE__，页面可能未正确加载")
                
                # 解析JSON字符串
                state = json.loads(state_json)
                
            except Exception as e:
                # 如果JSON序列化也失败，尝试只提取需要的部分
                print(f"⚠ 警告：完整序列化失败 ({str(e)[:100]}...)，尝试提取关键数据...")
                try:
                    # 只提取笔记相关的数据，避免序列化整个state
                    state_json = page.evaluate("""
                        () => {
                            const state = window.__INITIAL_STATE__;
                            if (!state) return null;
                            
                            // 只提取笔记相关的部分，避免循环引用和过大对象
                            const result = {};
                            if (state.note) {
                                result.note = state.note;
                            }
                            if (state.noteData) {
                                result.noteData = state.noteData;
                            }
                            if (state.noteDetail) {
                                result.noteDetail = state.noteDetail;
                            }
                            
                            // 尝试序列化，如果失败则返回null
                            try {
                                return JSON.stringify(result);
                            } catch (e) {
                                console.error('序列化失败:', e);
                                return null;
                            }
                        }
                    """)
                    
                    if state_json:
                        state = json.loads(state_json)
                    else:
                        raise RuntimeError("无法序列化 window.__INITIAL_STATE__，对象可能包含循环引用或过大")
                except Exception as e2:
                    raise RuntimeError(f"无法获取 window.__INITIAL_STATE__: {e2}")
            
            browser.close()
        
        # 解析state
        note = _parse_note_from_state(state, final_url)
        return note
        
    except Exception as e:
        raise RuntimeError(f"抓取笔记时出错: {e}")


def fetch_note_from_url(url: str, state_path: str = None) -> Note:
    """
    直接从URL抓取笔记（不需要分享文本）
    
    Args:
        url: 小红书笔记URL（可以是短链或完整链接）
        state_path: 登录态文件路径
    
    Returns:
        Note 对象
    """
    # 构造一个假的分享文本格式
    fake_share_text = f"笔记链接: {url} 复制后打开【小红书】查看笔记！"
    return fetch_note_from_share_text(fake_share_text, state_path)


if __name__ == "__main__":
    # CLI 测试
    import sys
    
    print("=" * 60)
    print("小红书笔记提取工具")
    print("=" * 60)
    
    # 检查登录态
    if not check_login_state_exists():
        print("\n❌ 错误：未找到登录态文件")
        print("请先运行登录脚本：")
        print("  python -m xhs_extractor_module.xhs_login")
        sys.exit(1)
    
    print("\n请输入小红书分享文本（包含链接）：")
    print("（可以直接粘贴完整的分享文案）")
    print("-" * 60)
    
    share = input().strip()
    
    if not share:
        print("❌ 错误：输入为空")
        sys.exit(1)
    
    try:
        note = fetch_note_from_share_text(share)
        
        print("\n" + "=" * 60)
        print("提取结果：")
        print("=" * 60)
        print(f"标题: {note.title}")
        print(f"正文长度: {len(note.text)} 字符")
        print(f"图片数量: {len(note.images)}")
        print(f"\n正文预览（前500字）:\n{note.text[:500]}...")
        
        if note.images:
            print(f"\n图片URL列表:")
            for i, img_url in enumerate(note.images[:5], 1):  # 只显示前5张
                print(f"  {i}. {img_url}")
            if len(note.images) > 5:
                print(f"  ... 还有 {len(note.images) - 5} 张图片")
        
        print("\n✅ 提取完成！")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

