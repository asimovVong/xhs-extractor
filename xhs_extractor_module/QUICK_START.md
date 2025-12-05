# 🚀 快速开始 - 3步提取小红书笔记

## 第一步：安装依赖

```bash
pip install playwright
playwright install chromium
```

## 第二步：首次登录（只需一次）

```bash
python -m xhs_extractor_module.xhs_login
```

这会打开浏览器，你完成登录后按回车即可。

## 第三步：提取笔记

### 方式1：交互式（最简单）

```bash
python -m xhs_extractor_module.cli
```

然后直接粘贴小红书分享文本即可！

### 方式2：命令行

```bash
python -m xhs_extractor_module.cli "算法面经... http://xhslink.com/o/ABC123 复制后打开"
```

## ✨ 完成！

就这么简单！工具会自动：
1. 提取分享文本中的链接
2. 使用保存的登录态访问页面
3. 解析出标题、正文、图片
4. 输出完整的文字内容

## 📖 更多功能

- **OCR识别图片文字**：添加 `--ocr` 参数
- **保存到文件**：添加 `--output result.txt` 参数
- **只输出文本**：添加 `--text-only` 参数

详细说明请查看 [CLI_USAGE.md](CLI_USAGE.md)

