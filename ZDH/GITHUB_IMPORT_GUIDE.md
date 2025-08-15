# 🚀 GitHub导入指南

## 📋 前置要求

### 1. 安装Git
```bash
# 下载Git for Windows
# 访问: https://git-scm.com/download/win
# 下载并安装Git for Windows
```

### 2. 安装完成后验证
```bash
git --version
```

## 🔧 本地Git初始化

### 1. 初始化Git仓库
```bash
# 在项目根目录下执行
git init
```

### 2. 配置Git用户信息
```bash
git config --global user.name "您的GitHub用户名"
git config --global user.email "您的邮箱地址"
```

### 3. 添加文件到Git
```bash
# 添加所有文件
git add .

# 或者选择性添加
git add README.md
git add *.py
git add requirements.txt
git add .gitignore
git add LICENSE
```

### 4. 创建首次提交
```bash
git commit -m "Initial commit: ZDH智能自动化测试系统

- 集成AI驱动的测试用例生成
- 支持多维度自动化（文件、应用、网页、UI）
- 智能前置条件执行
- 完整的测试报告系统
- OCR图像识别优化
- 统一自动化框架"
```

## 🌐 GitHub仓库创建

### 1. 登录GitHub
- 访问: https://github.com
- 使用您的GitHub账号登录

### 2. 创建新仓库
- 点击右上角的 "+" 号
- 选择 "New repository"
- 填写仓库信息：
  - **Repository name**: `ZDH-Automation-Testing-System`
  - **Description**: `基于AI的Windows平台智能自动化测试系统，支持贝壳库纯画图界面`
  - **Visibility**: 选择 Public 或 Private
  - **不要**勾选 "Add a README file"（因为我们已经有了）
  - **不要**勾选 "Add .gitignore"（因为我们已经有了）
  - **不要**勾选 "Choose a license"（因为我们已经有了）

### 3. 创建仓库
- 点击 "Create repository"

## 🔗 连接本地仓库到GitHub

### 方法1: 使用HTTPS（推荐新手）
```bash
# 添加远程仓库
git remote add origin https://github.com/您的用户名/ZDH-Automation-Testing-System.git

# 推送代码到GitHub
git branch -M main
git push -u origin main
```

### 方法2: 使用SSH（推荐高级用户）
```bash
# 生成SSH密钥（如果还没有）
ssh-keygen -t ed25519 -C "您的邮箱地址"

# 添加SSH密钥到GitHub
# 1. 复制公钥内容
cat ~/.ssh/id_ed25519.pub

# 2. 在GitHub设置中添加SSH密钥
# Settings -> SSH and GPG keys -> New SSH key

# 添加远程仓库
git remote add origin git@github.com:您的用户名/ZDH-Automation-Testing-System.git

# 推送代码到GitHub
git branch -M main
git push -u origin main
```

## 📝 仓库设置优化

### 1. 添加仓库描述
在GitHub仓库页面：
- 点击 "About" 部分
- 添加详细描述
- 添加网站链接（如果有）
- 添加主题标签（Topics）

### 2. 设置仓库主题标签
建议添加以下标签：
- `automation-testing`
- `ai-driven`
- `windows-automation`
- `ocr-recognition`
- `python`
- `ui-automation`
- `test-automation`
- `beike-library`

### 3. 配置分支保护（可选）
- 进入 Settings -> Branches
- 添加分支保护规则
- 保护 main 分支

## 🔄 后续维护

### 1. 日常更新流程
```bash
# 查看状态
git status

# 添加更改
git add .

# 提交更改
git commit -m "描述您的更改"

# 推送到GitHub
git push
```

### 2. 创建新分支
```bash
# 创建并切换到新分支
git checkout -b feature/新功能名称

# 开发完成后合并到主分支
git checkout main
git merge feature/新功能名称
git push
```

### 3. 处理冲突
```bash
# 拉取最新代码
git pull origin main

# 如果有冲突，手动解决后
git add .
git commit -m "解决冲突"
git push
```

## 📊 仓库统计和徽章

### 1. 添加徽章到README
在README.md顶部添加徽章：
```markdown
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/Platform-Windows-green.svg)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/您的用户名/ZDH-Automation-Testing-System.svg)](https://github.com/您的用户名/ZDH-Automation-Testing-System/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/您的用户名/ZDH-Automation-Testing-System.svg)](https://github.com/您的用户名/ZDH-Automation-Testing-System/network)
```

### 2. 启用GitHub Pages（可选）
- 进入 Settings -> Pages
- 选择 Source: Deploy from a branch
- 选择 Branch: main
- 选择文件夹: / (root)
- 点击 Save

## 🚨 注意事项

### 1. 敏感信息保护
- 确保 `.env` 文件在 `.gitignore` 中
- 不要提交API密钥、密码等敏感信息
- 使用环境变量或配置文件管理敏感数据

### 2. 大文件处理
- 避免提交大文件（>100MB）
- 使用 Git LFS 处理大文件
- 定期清理临时文件和日志

### 3. 提交信息规范
使用清晰的提交信息：
```bash
git commit -m "feat: 添加AI前置条件执行功能"
git commit -m "fix: 修复OCR识别精度问题"
git commit -m "docs: 更新README文档"
git commit -m "refactor: 重构自动化框架结构"
```

## 🎉 完成

恭喜！您的ZDH项目现在已经成功导入到GitHub。您可以：

1. 分享仓库链接给其他人
2. 接受贡献者的Pull Request
3. 使用GitHub Issues跟踪问题
4. 使用GitHub Actions进行CI/CD
5. 使用GitHub Wiki编写详细文档

## 📞 获取帮助

如果遇到问题：
1. 查看GitHub官方文档
2. 搜索Stack Overflow
3. 在GitHub Issues中提问
4. 联系项目维护者
