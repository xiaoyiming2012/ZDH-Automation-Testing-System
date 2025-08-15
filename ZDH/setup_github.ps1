# ZDH项目GitHub导入助手 - PowerShell版本
# 使用方法: 右键点击 -> "使用PowerShell运行"

param(
    [switch]$Help,
    [switch]$SkipChecks
)

# 设置控制台编码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Show-Help {
    Write-Host @"
🚀 ZDH项目GitHub导入助手 - PowerShell版本

使用方法:
    .\setup_github.ps1                    # 正常运行
    .\setup_github.ps1 -SkipChecks        # 跳过环境检查
    .\setup_github.ps1 -Help              # 显示帮助信息

前置要求:
    1. Python 3.11+
    2. Git for Windows
    3. 在ZDH项目根目录下运行

"@ -ForegroundColor Cyan
}

function Test-Environment {
    Write-Host "🔍 检查环境..." -ForegroundColor Yellow
    
    # 检查Python
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
        } else {
            Write-Host "❌ Python未正确安装" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ 未检测到Python，请先安装Python 3.11+" -ForegroundColor Red
        Write-Host "下载地址: https://www.python.org/downloads/" -ForegroundColor Yellow
        return $false
    }
    
    # 检查Git
    try {
        $gitVersion = git --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Git: $gitVersion" -ForegroundColor Green
        } else {
            Write-Host "❌ Git未正确安装" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ 未检测到Git，请先安装Git for Windows" -ForegroundColor Red
        Write-Host "下载地址: https://git-scm.com/download/win" -ForegroundColor Yellow
        return $false
    }
    
    # 检查项目目录
    if (-not (Test-Path "README.md")) {
        Write-Host "❌ 请在ZDH项目根目录下运行此脚本" -ForegroundColor Red
        return $false
    }
    
    Write-Host "✅ 环境检查通过" -ForegroundColor Green
    return $true
}

function Initialize-GitRepository {
    Write-Host "🔧 初始化Git仓库..." -ForegroundColor Yellow
    
    if (Test-Path ".git") {
        Write-Host "ℹ️ Git仓库已存在" -ForegroundColor Blue
        return $true
    }
    
    try {
        git init
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Git仓库初始化成功" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ Git仓库初始化失败" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ Git仓库初始化异常: $_" -ForegroundColor Red
        return $false
    }
}

function Configure-GitUser {
    Write-Host "📝 配置Git用户信息..." -ForegroundColor Yellow
    
    $username = Read-Host "请输入您的GitHub用户名"
    $email = Read-Host "请输入您的邮箱地址"
    
    if ([string]::IsNullOrWhiteSpace($username) -or [string]::IsNullOrWhiteSpace($email)) {
        Write-Host "❌ 用户名和邮箱不能为空" -ForegroundColor Red
        return $false
    }
    
    try {
        git config --global user.name $username
        git config --global user.email $email
        
        Write-Host "✅ Git用户信息配置成功" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "❌ Git用户信息配置失败: $_" -ForegroundColor Red
        return $false
    }
}

function Add-FilesToGit {
    Write-Host "📁 添加文件到Git..." -ForegroundColor Yellow
    
    if (-not (Test-Path ".gitignore")) {
        Write-Host "⚠️ .gitignore文件不存在，建议先创建" -ForegroundColor Yellow
    }
    
    try {
        git add .
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ 文件添加成功" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ 文件添加失败" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ 文件添加异常: $_" -ForegroundColor Red
        return $false
    }
}

function Create-InitialCommit {
    Write-Host "💾 创建首次提交..." -ForegroundColor Yellow
    
    $commitMessage = @"
Initial commit: ZDH智能自动化测试系统

- 集成AI驱动的测试用例生成
- 支持多维度自动化（文件、应用、网页、UI）
- 智能前置条件执行
- 完整的测试报告系统
- OCR图像识别优化
- 统一自动化框架
"@
    
    try {
        git commit -m $commitMessage
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ 首次提交创建成功" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ 首次提交创建失败" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ 首次提交创建异常: $_" -ForegroundColor Red
        return $false
    }
}

function Setup-GitHubRemote {
    Write-Host "🌐 设置GitHub远程仓库..." -ForegroundColor Yellow
    
    Write-Host @"

📋 请在GitHub上创建新仓库:
1. 访问: https://github.com
2. 点击右上角 '+' -> New repository
3. 仓库名: ZDH-Automation-Testing-System
4. 描述: 基于AI的Windows平台智能自动化测试系统
5. 选择 Public 或 Private
6. 不要勾选任何初始化选项
7. 点击 Create repository

"@ -ForegroundColor Cyan
    
    Read-Host "按回车键继续"
    
    $username = Read-Host "请输入您的GitHub用户名"
    if ([string]::IsNullOrWhiteSpace($username)) {
        Write-Host "❌ 用户名不能为空" -ForegroundColor Red
        return $false
    }
    
    Write-Host @"

🔗 选择连接方式:
1. HTTPS (推荐新手)
2. SSH (推荐高级用户)

"@ -ForegroundColor Cyan
    
    $choice = Read-Host "请选择 (1 或 2)"
    
    if ($choice -eq "2") {
        $remoteUrl = "git@github.com:$username/ZDH-Automation-Testing-System.git"
    } else {
        $remoteUrl = "https://github.com/$username/ZDH-Automation-Testing-System.git"
    }
    
    try {
        git remote add origin $remoteUrl
        git branch -M main
        
        Write-Host "✅ GitHub远程仓库设置成功" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "❌ GitHub远程仓库设置失败: $_" -ForegroundColor Red
        return $false
    }
}

function Push-ToGitHub {
    Write-Host "🚀 推送到GitHub..." -ForegroundColor Yellow
    
    try {
        git push -u origin main
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ 代码推送成功" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ 代码推送失败" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ 代码推送异常: $_" -ForegroundColor Red
        return $false
    }
}

function Show-NextSteps {
    Write-Host @"

🎉 GitHub导入设置完成！

📋 后续建议:
1. 在GitHub仓库页面添加主题标签 (Topics)
2. 配置分支保护规则
3. 启用GitHub Pages (可选)
4. 设置GitHub Actions (可选)

🔗 相关文档:
- GitHub导入指南: GITHUB_IMPORT_GUIDE.md
- 项目说明: README.md
- 技术设计: technical_design.md

"@ -ForegroundColor Green
}

# 主函数
function Main {
    Write-Host @"
========================================
🚀 ZDH项目GitHub导入助手
========================================

"@ -ForegroundColor Cyan
    
    # 显示帮助
    if ($Help) {
        Show-Help
        return
    }
    
    # 环境检查
    if (-not $SkipChecks) {
        if (-not (Test-Environment)) {
            Write-Host "❌ 环境检查失败，请解决上述问题后重试" -ForegroundColor Red
            Read-Host "按回车键退出"
            return
        }
    }
    
    Write-Host ""
    
    # 执行GitHub导入流程
    $steps = @(
        @{ Name = "初始化Git仓库"; Function = "Initialize-GitRepository" },
        @{ Name = "配置Git用户"; Function = "Configure-GitUser" },
        @{ Name = "添加文件到Git"; Function = "Add-FilesToGit" },
        @{ Name = "创建首次提交"; Function = "Create-InitialCommit" },
        @{ Name = "设置GitHub远程仓库"; Function = "Setup-GitHubRemote" },
        @{ Name = "推送到GitHub"; Function = "Push-ToGitHub" }
    )
    
    foreach ($step in $steps) {
        Write-Host "`n🔄 执行: $($step.Name)" -ForegroundColor Yellow
        
        $functionName = $step.Function
        $result = & $functionName
        
        if (-not $result) {
            Write-Host "❌ $($step.Name)失败，停止执行" -ForegroundColor Red
            Read-Host "按回车键退出"
            return
        }
        
        Write-Host "✅ $($step.Name)完成" -ForegroundColor Green
    }
    
    # 显示后续步骤
    Show-NextSteps
    
    Read-Host "按回车键退出"
}

# 执行主函数
try {
    Main
} catch {
    Write-Host "❌ 发生错误: $_" -ForegroundColor Red
    Read-Host "按回车键退出"
}
