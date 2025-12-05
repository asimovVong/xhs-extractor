#!/bin/bash
# 从项目根目录启动Web应用的便捷脚本

cd "$(dirname "$0")"

echo "🚀 启动小红书笔记提取Web应用..."
echo ""

# 检查是否安装了streamlit
if ! python -c "import streamlit" 2>/dev/null; then
    echo "❌ 未安装 streamlit"
    echo "正在安装..."
    pip install streamlit
fi

# 检查登录态
if [ ! -f "xhs_extractor_module/xhs_state.json" ]; then
    echo "⚠️  警告: 未找到登录态文件"
    echo "请先运行: python -m xhs_extractor_module.xhs_login"
    echo ""
    read -p "是否现在登录? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python -m xhs_extractor_module.xhs_login
    fi
fi

# 启动Web应用
echo "📱 正在启动Web应用..."
echo "浏览器将自动打开 http://localhost:8501"
echo ""
streamlit run xhs_extractor_module/web_app.py

