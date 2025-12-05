# OCR 图片文字识别使用指南

## 🎯 快速开始

### 1. 安装 OCR 依赖

```bash
pip install paddleocr paddlepaddle
```

**注意：**
- macOS 用户可能需要额外安装系统依赖
- 首次使用 OCR 时会自动下载模型文件（约 100MB+），请耐心等待

### 2. 使用 OCR 功能

#### 方式1：命令行参数

```bash
# 启用OCR识别图片文字
python -m xhs_extractor_module.cli --ocr "分享文本..."

# 或从URL提取
python -m xhs_extractor_module.cli --ocr --url "http://xhslink.com/o/ABC123"
```

#### 方式2：交互式模式

```bash
python -m xhs_extractor_module.cli
# 然后输入 'ocr' 切换OCR模式
# 再粘贴分享文本
```

## 📝 使用示例

### 基本使用

```bash
# 提取笔记（不包含OCR）
python -m xhs_extractor_module.cli "分享文本..."

# 提取笔记（包含OCR）
python -m xhs_extractor_module.cli --ocr "分享文本..."
```

### 输出对比

**不使用OCR：**
```
📊 统计信息
标题长度: 21 字符
正文长度: 52 字符
图片数量: 18
```

**使用OCR：**
```
📊 统计信息
标题长度: 21 字符
正文长度: 52 字符
OCR文本长度: 1234 字符
总文本长度: 1307 字符
图片数量: 18

📄 完整文本内容
[正文内容]

[图片文字识别]
[图片 1 OCR 结果]
识别出的文字内容...
[图片 2 OCR 结果]
...
```

## ⚙️ OCR 处理流程

1. **下载图片**：从图片URL下载到临时文件
2. **OCR识别**：使用PaddleOCR识别图片中的文字
3. **合并文本**：将所有图片的OCR结果合并
4. **清理临时文件**：自动删除临时文件

## 🔧 故障排除

### 问题1：提示"未安装 paddleocr"

**解决方案：**
```bash
pip install paddleocr paddlepaddle
```

### 问题2：OCR初始化失败

**可能原因：**
- 系统缺少依赖库
- 网络问题（首次使用需要下载模型）

**解决方案：**
- macOS: `brew install opencv`（如果报错）
- 检查网络连接
- 首次使用请耐心等待模型下载

### 问题3：OCR识别结果为空

**可能原因：**
- 图片中没有文字
- 图片质量太低
- 图片格式不支持

**解决方案：**
- 检查图片是否包含文字
- 尝试其他图片

### 问题4：OCR速度慢

**说明：**
- OCR处理需要时间，特别是多张图片
- 18张图片可能需要几分钟时间

**优化建议：**
- 如果不需要OCR，可以不使用 `--ocr` 参数
- 只对包含重要文字的图片使用OCR

## 💡 最佳实践

1. **按需使用**：如果笔记主要是文字内容，不需要OCR
2. **批量处理**：对于包含大量图片的笔记，OCR可能需要较长时间
3. **保存结果**：使用 `--output` 参数保存结果，避免重复OCR

```bash
# 保存OCR结果到文件
python -m xhs_extractor_module.cli --ocr --output result.txt "分享文本..."
```

## 📚 相关文档

- [README.md](README.md) - 模块总体说明
- [CLI_USAGE.md](CLI_USAGE.md) - CLI使用指南
- [QUICK_START.md](QUICK_START.md) - 快速开始

