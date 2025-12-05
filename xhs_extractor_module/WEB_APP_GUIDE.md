# Web前端使用指南

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install streamlit
```

或安装所有依赖：

```bash
pip install -r requirements.txt
```

### 2. 启动Web应用

**方式1：从项目根目录启动（推荐）**

```bash
# 确保在项目根目录
cd /Users/asimov/project/xhs

# 启动Web应用
streamlit run xhs_extractor_module/web_app.py
```

**方式2：使用便捷脚本**

```bash
# 从项目根目录运行
./start_web.sh
```

浏览器会自动打开 `http://localhost:8501`

## 📋 功能说明

### 主要功能

1. **输入小红书链接**
   - 支持直接输入URL（完整链接或短链接）
   - 支持粘贴分享文本

2. **选择功能选项**
   - ✅ OCR识别图片文字：识别图片中的文字内容
   - ✅ 下载图片到本地：将笔记中的图片下载到本地
   - ✅ 下载笔记正文：将笔记正文保存为Markdown文件

3. **选择保存位置**
   - 可以自定义保存目录
   - 默认保存到 `~/Downloads/xhs_notes/`

4. **自动组织文件**
   - 自动创建以笔记标题命名的文件夹
   - Markdown文件名为笔记标题
   - 图片按顺序命名：`image_001.jpg`, `image_002.jpg` 等

## 🎯 使用流程

1. **启动应用**
   ```bash
   streamlit run xhs_extractor_module/web_app.py
   ```

2. **输入链接**
   - 在输入框中粘贴小红书链接或分享文本

3. **选择选项**
   - 在侧边栏勾选需要的功能：
     - OCR识别（需要安装paddleocr）
     - 下载图片
     - 下载正文（默认启用）

4. **设置保存位置**
   - 在侧边栏输入保存目录路径
   - 或使用默认路径

5. **开始提取**
   - 点击"🚀 开始提取"按钮
   - 等待提取完成

6. **查看结果**
   - 预览笔记内容
   - 查看OCR识别结果（如果启用）
   - 查看保存的文件列表

## 📁 文件结构

保存后的文件结构示例：

```
保存目录/
└── 笔记标题/
    ├── 笔记标题.md          # 笔记正文（Markdown格式）
    ├── image_001.jpg        # 图片1
    ├── image_002.jpg        # 图片2
    └── ...
```

## 📝 Markdown文件格式

保存的Markdown文件包含：

```markdown
# 笔记标题

**链接**: https://www.xiaohongshu.com/explore/...

**笔记ID**: abc123

---

## 正文

笔记正文内容...

---

## 图片文字识别

OCR识别的文字内容...

---

## 图片

![图片 1](image_001.jpg)
![图片 2](image_002.jpg)
```

## ⚙️ 配置选项

### OCR识别

- **启用条件**: 勾选"OCR识别图片文字"
- **前置要求**: 需要安装 `paddleocr` 和 `paddlepaddle`
- **处理时间**: 根据图片数量，可能需要几分钟

### 下载图片

- **启用条件**: 勾选"下载图片到本地"
- **文件格式**: 自动识别（jpg/png/gif/webp）
- **文件命名**: 按顺序命名 `image_001.jpg`, `image_002.jpg` 等

### 下载正文

- **默认启用**: 默认勾选
- **文件格式**: Markdown (.md)
- **文件命名**: 笔记标题

## 🔧 故障排除

### 问题1：无法启动Web应用

**错误**: `streamlit: command not found`

**解决方案**:
```bash
pip install streamlit
```

### 问题2：端口被占用

**错误**: `Port 8501 is already in use`

**解决方案**:
```bash
# 使用其他端口
streamlit run xhs_extractor_module/web_app.py --server.port 8502
```

### 问题3：未找到登录态

**错误**: 提示"未找到登录态文件"

**解决方案**:
```bash
python -m xhs_extractor_module.xhs_login
```

### 问题4：OCR功能不可用

**错误**: "OCR功能不可用：未安装 paddleocr"

**解决方案**:
```bash
pip install paddleocr paddlepaddle
```

### 问题5：文件保存失败

**可能原因**:
- 目录权限不足
- 磁盘空间不足
- 文件名包含非法字符（已自动处理）

**解决方案**:
- 检查目录权限
- 检查磁盘空间
- 使用其他保存目录

## 💡 使用技巧

1. **批量处理**: 可以多次提取不同的笔记，每次都会创建新的文件夹

2. **预览内容**: 在保存前可以先预览笔记内容，确认无误后再保存

3. **选择性下载**: 
   - 如果只需要文字内容，可以不下载图片
   - 如果图片不重要，可以不启用OCR

4. **自定义保存位置**: 
   - 可以设置不同的保存目录
   - 建议使用绝对路径

## 📚 相关文档

- [README.md](README.md) - 模块总体说明
- [CLI_USAGE.md](CLI_USAGE.md) - 命令行使用指南
- [OCR_GUIDE.md](OCR_GUIDE.md) - OCR使用指南

## 🎨 界面预览

Web界面包含：

- **主界面**: 输入框、提取按钮、结果预览
- **侧边栏**: 功能选项、保存位置设置
- **结果展示**: 笔记信息、内容预览、文件列表

界面简洁易用，支持实时预览和进度显示。

