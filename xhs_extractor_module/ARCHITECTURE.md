# 小红书笔记提取模块 - 架构设计文档

## 📋 概述

这是一个完整的小红书（Xiaohongshu）笔记内容提取模块，支持从链接自动提取文本和图片内容，并对图片进行 OCR 文字识别。

## 🏗️ 架构设计

### 核心模块

```
xhs_extractor_module/
├── xhs_parser.py          # 小红书链接解析器
├── ocr.py                 # OCR 图片文字识别
├── cookie_manager.py      # Cookie 管理
├── models.py              # 数据模型（Note）
└── example_usage.py       # 使用示例
```

### 数据流

```
用户输入链接
    ↓
[xhs_parser] 解析链接 → 提取 HTML
    ↓
解析 __INITIAL_STATE__ → 提取文本和图片 URL
    ↓
[ocr] 下载图片 → OCR 识别文字
    ↓
合并文本 + OCR文本 → Note 对象
    ↓
返回给调用方
```

## 🔑 核心设计理念

### 1. Cookie 管理策略

**设计思路：**
- **自动尝试**：首次访问时自动尝试（可能失败）
- **快速失败**：没有 Cookie 时，3 秒超时，快速提示用户
- **持久化存储**：成功使用的 Cookie 自动保存到本地
- **格式灵活**：支持浏览器原生 Cookie 字符串格式（从 Network 面板复制）

**实现要点：**
```python
# 优先级顺序：
1. 用户手动输入的 cookie_string（最高优先级）
2. 已保存的 cookies（从文件加载）
3. 无 Cookie 尝试（快速失败）

# Cookie 格式转换：
浏览器格式: "a1=xxx; web_session=yyy; webId=zzz"
    ↓ parse_cookie_string()
字典格式: {"a1": "xxx", "web_session": "yyy", "webId": "zzz"}
    ↓ save_cookies()
保存到文件: cookies/xhs_cookies_latest.json
    ↓ load_saved_cookies()
下次使用: 自动加载
```

### 2. 内容提取策略

**多层提取方案：**

1. **优先从 `__INITIAL_STATE__` 提取**（最可靠）
   - 小红书页面会注入一个 JavaScript 全局变量 `window.__INITIAL_STATE__`
   - 包含完整的笔记数据（标题、正文、图片列表等）
   - 使用正则表达式提取 JSON 数据

2. **从 HTML DOM 提取**（兜底方案）
   - 如果 `__INITIAL_STATE__` 不可用，使用 BeautifulSoup 解析 HTML
   - 查找常见的内容容器选择器
   - 提取所有文本内容

3. **图片 URL 提取**
   - 支持多种数据结构（`imageList`, `images`, `imageInfo` 等）
   - 自动去重
   - 过滤无效 URL

**代码示例：**
```python
# 从 __INITIAL_STATE__ 提取
match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.+?})\s*</script>', script.string)
initial_state = json.loads(match.group(1))
note_data = initial_state.get('note', {}) or initial_state.get('noteDetail', {})

# 多路径尝试获取图片
img_url = (
    img.get('url') or 
    img.get('urlDefault') or 
    img.get('picUrl') or 
    img.get('info', {}).get('url') or
    ...
)
```

### 3. OCR 处理策略

**设计思路：**
- **可选依赖**：PaddleOCR 是可选的，没有安装也能运行（只提取文本）
- **流式下载**：使用 `stream=True` 下载大图片
- **临时文件管理**：使用 `tempfile` 创建临时文件，使用后自动清理
- **错误处理**：OCR 失败不影响整体流程（只是没有 OCR 文本）

**实现要点：**
```python
# 支持多种图片格式
content_type = response.headers.get('Content-Type', '').lower()
if 'png' in content_type:
    suffix = '.png'
elif 'gif' in content_type:
    suffix = '.gif'
else:
    suffix = '.jpg'

# 流式下载
for chunk in response.iter_content(chunk_size=8192):
    tmp_file.write(chunk)

# 确保清理临时文件
try:
    text = self.ocr_image_from_file(tmp_path)
finally:
    os.unlink(tmp_path)
```

### 4. 错误处理和用户引导

**设计思路：**
- **智能检测**：自动检测是否需要登录（通过内容长度和关键词）
- **友好提示**：提供详细的操作指引
- **多种方案**：提供多种处理方式（Cookie、手动输入文本等）

**检测逻辑：**
```python
login_keywords = ['登录', '注册', '发现发布通知登录我', '请登录', '登录查看']
if not text or len(text) < 20 or any(keyword in text for keyword in login_keywords):
    # 检测到需要登录
    print("⚠ 警告：检测到可能需要登录才能查看完整内容")
```

## 🔐 Cookie 获取流程设计

### 前端流程

```
用户输入链接
    ↓
[检测是否为小红书链接]
    ↓
[快速尝试访问] (3秒超时)
    ↓
成功？ → [直接提取]
    ↓
失败？
    ↓
[显示登录引导模态框]
    ↓
用户选择：
  1. 在新窗口登录 → 复制 Cookie → 手动输入
  2. 复制内容 → 切换到文本输入模式（推荐）
  3. 已登录 → 重新尝试
```

### 后端流程

```
收到请求
    ↓
[优先级检查]
  1. cookie_string (请求中提供)
  2. load_saved_cookies() (从文件加载)
  3. None (无 Cookie 尝试)
    ↓
[访问链接]
    ↓
成功？
    ↓
是 → [保存 Cookie] → [提取内容]
    ↓
否 → [返回 needs_cookie: true] → [前端显示引导]
```

## 📦 数据模型

### Note 对象

```python
@dataclass
class Note:
    id: str                    # 笔记 ID（从 URL 提取或生成 UUID）
    url: str                   # 笔记链接
    title: str                 # 笔记标题
    text: str                  # 文本内容（正文）
    ocr_text: str              # OCR 识别的文字（图片中的文字）
    images: List[str]          # 图片 URL 列表
    raw: Dict[str, Any]        # 原始数据（调试用）
```

## 🎯 关键设计决策

### 1. 为什么使用 Cookie 字符串而不是字典？

**原因：**
- 用户直接从浏览器 Network 面板复制的是字符串格式
- 减少格式转换的复杂度
- 更符合实际使用场景

### 2. 为什么缩短无 Cookie 时的超时时间？

**原因：**
- 避免用户长时间等待
- 快速提示需要登录
- 提供更好的用户体验

### 3. 为什么使用多层提取策略？

**原因：**
- 小红书页面结构可能变化
- 不同页面可能使用不同的数据结构
- 提高容错性和健壮性

### 4. 为什么 OCR 是可选的？

**原因：**
- PaddleOCR 安装复杂，需要系统依赖
- 不是所有场景都需要 OCR
- 降低使用门槛

## 🚀 性能优化

1. **并发处理**：多张图片可以并发下载和 OCR（未实现，可扩展）
2. **缓存机制**：Cookie 持久化，避免重复获取
3. **流式下载**：大图片使用流式下载，节省内存
4. **快速失败**：无 Cookie 时快速失败，避免长时间等待

## 🔧 扩展性设计

1. **OCR 引擎可替换**：支持多种 OCR 引擎（目前是 PaddleOCR）
2. **Cookie 存储可替换**：可以扩展为数据库存储
3. **提取策略可扩展**：可以添加更多的提取方法
4. **错误处理可定制**：可以根据需求定制错误处理逻辑

## 📝 注意事项

1. **Cookie 有效期**：Cookie 会过期，需要定期更新
2. **反爬虫机制**：小红书可能有反爬虫机制，需要合理使用
3. **法律合规**：遵守网站服务条款和相关法律法规
4. **隐私保护**：Cookie 包含用户信息，需要妥善保管

