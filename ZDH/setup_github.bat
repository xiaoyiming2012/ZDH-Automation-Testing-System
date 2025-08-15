@echo off
chcp 65001 >nul
title ZDH项目GitHub导入助手

echo.
echo ========================================
echo 🚀 ZDH项目GitHub导入助手
echo ========================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到Python，请先安装Python 3.11+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 检查Git是否安装
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到Git，请先安装Git for Windows
    echo 下载地址: https://git-scm.com/download/win
    echo.
    echo 安装完成后请重新运行此脚本
    pause
    exit /b 1
)

echo ✅ 环境检查通过
echo.

:: 运行Python脚本
echo 🔄 启动GitHub导入助手...
python setup_github.py

echo.
echo ========================================
echo 📋 操作完成
echo ========================================
echo.
echo 如果遇到问题，请查看:
echo - GITHUB_IMPORT_GUIDE.md (详细指南)
echo - README.md (项目说明)
echo.
pause
