#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub仓库快速设置脚本
帮助用户快速将ZDH项目导入到GitHub
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """运行命令并处理结果"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            print(f"✅ {description}成功")
            if result.stdout.strip():
                print(f"   输出: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description}失败")
            if result.stderr.strip():
                print(f"   错误: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description}异常: {e}")
        return False

def check_git_installed():
    """检查Git是否已安装"""
    print("🔍 检查Git安装状态...")
    return run_command("git --version", "Git版本检查")

def init_git_repo():
    """初始化Git仓库"""
    if os.path.exists(".git"):
        print("ℹ️ Git仓库已存在")
        return True
    
    return run_command("git init", "初始化Git仓库")

def configure_git_user():
    """配置Git用户信息"""
    print("📝 配置Git用户信息...")
    
    # 获取用户输入
    username = input("请输入您的GitHub用户名: ").strip()
    email = input("请输入您的邮箱地址: ").strip()
    
    if not username or not email:
        print("❌ 用户名和邮箱不能为空")
        return False
    
    # 配置用户信息
    success1 = run_command(f'git config --global user.name "{username}"', "设置用户名")
    success2 = run_command(f'git config --global user.email "{email}"', "设置邮箱")
    
    return success1 and success2

def add_files_to_git():
    """添加文件到Git"""
    print("📁 添加文件到Git...")
    
    # 检查.gitignore是否存在
    if not os.path.exists(".gitignore"):
        print("⚠️ .gitignore文件不存在，建议先创建")
    
    # 添加所有文件
    return run_command("git add .", "添加所有文件到Git")

def create_initial_commit():
    """创建首次提交"""
    commit_message = """Initial commit: ZDH智能自动化测试系统

- 集成AI驱动的测试用例生成
- 支持多维度自动化（文件、应用、网页、UI）
- 智能前置条件执行
- 完整的测试报告系统
- OCR图像识别优化
- 统一自动化框架"""
    
    return run_command(f'git commit -m "{commit_message}"', "创建首次提交")

def setup_github_remote():
    """设置GitHub远程仓库"""
    print("🌐 设置GitHub远程仓库...")
    
    print("\n📋 请在GitHub上创建新仓库:")
    print("1. 访问: https://github.com")
    print("2. 点击右上角 '+' -> New repository")
    print("3. 仓库名: ZDH-Automation-Testing-System")
    print("4. 描述: 基于AI的Windows平台智能自动化测试系统")
    print("5. 选择 Public 或 Private")
    print("6. 不要勾选任何初始化选项")
    print("7. 点击 Create repository")
    
    input("\n按回车键继续...")
    
    # 获取仓库URL
    username = input("请输入您的GitHub用户名: ").strip()
    if not username:
        print("❌ 用户名不能为空")
        return False
    
    # 选择连接方式
    print("\n🔗 选择连接方式:")
    print("1. HTTPS (推荐新手)")
    print("2. SSH (推荐高级用户)")
    
    choice = input("请选择 (1 或 2): ").strip()
    
    if choice == "1":
        remote_url = f"https://github.com/{username}/ZDH-Automation-Testing-System.git"
    elif choice == "2":
        remote_url = f"git@github.com:{username}/ZDH-Automation-Testing-System.git"
    else:
        print("❌ 无效选择，使用HTTPS")
        remote_url = f"https://github.com/{username}/ZDH-Automation-Testing-System.git"
    
    # 添加远程仓库
    success1 = run_command(f'git remote add origin "{remote_url}"', "添加远程仓库")
    
    if success1:
        # 设置主分支名称
        success2 = run_command("git branch -M main", "设置主分支名称")
        return success2
    
    return False

def push_to_github():
    """推送到GitHub"""
    print("🚀 推送到GitHub...")
    
    # 首次推送
    return run_command("git push -u origin main", "首次推送到GitHub")

def show_next_steps():
    """显示后续步骤"""
    print("\n🎉 GitHub导入设置完成！")
    print("\n📋 后续建议:")
    print("1. 在GitHub仓库页面添加主题标签 (Topics)")
    print("2. 配置分支保护规则")
    print("3. 启用GitHub Pages (可选)")
    print("4. 设置GitHub Actions (可选)")
    print("\n🔗 相关文档:")
    print("- GitHub导入指南: GITHUB_IMPORT_GUIDE.md")
    print("- 项目说明: README.md")
    print("- 技术设计: technical_design.md")

def main():
    """主函数"""
    print("🚀 ZDH项目GitHub导入助手")
    print("=" * 50)
    
    # 检查当前目录
    current_dir = Path.cwd()
    if not (current_dir / "README.md").exists():
        print("❌ 请在ZDH项目根目录下运行此脚本")
        return
    
    print(f"📍 当前目录: {current_dir}")
    print(f"📁 项目文件: {len(list(current_dir.glob('*.py')))} 个Python文件")
    
    # 检查Git安装
    if not check_git_installed():
        print("\n❌ 请先安装Git:")
        print("下载地址: https://git-scm.com/download/win")
        return
    
    # 初始化Git仓库
    if not init_git_repo():
        return
    
    # 配置Git用户
    if not configure_git_user():
        return
    
    # 添加文件
    if not add_files_to_git():
        return
    
    # 创建提交
    if not create_initial_commit():
        return
    
    # 设置远程仓库
    if not setup_github_remote():
        return
    
    # 推送到GitHub
    if not push_to_github():
        return
    
    # 显示后续步骤
    show_next_steps()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断操作")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        print("请检查错误信息并重试")
