# 前置条件检查功能指南

## 概述

本框架现在具备智能前置条件检查功能，能够自动检测测试环境是否满足测试用例的执行条件，特别是软件安装状态和运行状态。

## 主要功能

### 1. 软件安装检查
- 检查软件是否已安装在系统中
- 支持多种安装路径检查
- 支持注册表检查（Windows系统）

### 2. 软件运行状态检查
- 检查软件进程是否正在运行
- 检查软件窗口是否存在
- 自动启动未运行的软件

### 3. 智能前置条件解析
- 从测试用例描述中自动提取前置条件
- 根据产品信息自动生成相关前置条件
- 支持极光PDF、Adobe Reader、WPS等常见软件

## 支持的软件

### 极光PDF
- 进程名：`JiGuangPDF.exe`, `JiGuangPDFReader.exe`
- 安装路径：`C:\Program Files\JiGuangPDF`
- 自动前置条件：
  - 极光PDF已安装
  - 打开PDF阅读器界面
  - 打开文件
  - 选取一段文字
  - 右键点击选取文字区域

### Adobe Reader
- 进程名：`AcroRd32.exe`, `AcroRd64.exe`
- 安装路径：`C:\Program Files\Adobe\Acrobat Reader`
- 自动前置条件：同上

### WPS Office
- 进程名：`wps.exe`, `wpp.exe`, `et.exe`
- 安装路径：`C:\Program Files\WPS Office`
- 自动前置条件：
  - WPS已安装
  - 打开WPS界面
  - 打开文件

## 使用方法

### 1. 基本使用

```python
from unified_automation_framework import UnifiedAutomationFramework

# 创建框架实例
framework = UnifiedAutomationFramework()

# 执行测试用例（自动检查前置条件）
result = framework.execute_test_case(test_case)
```

### 2. 手动检查前置条件

```python
# 检查软件是否安装
if framework.check_software_installed("极光PDF"):
    print("极光PDF已安装")

# 检查软件是否运行
if framework.check_software_running("极光PDF"):
    print("极光PDF正在运行")

# 启动软件（如果未运行）
if framework.launch_software_if_needed("极光PDF"):
    print("极光PDF启动成功")
```

### 3. 自定义软件配置

```python
# 添加新的软件配置
framework.software_configs["新软件"] = {
    "process_names": ["newapp.exe"],
    "window_titles": ["新软件"],
    "install_paths": ["C:\\Program Files\\新软件"]
}
```

## 测试前置条件检查功能

运行测试脚本验证功能：

```bash
python test_precondition_check.py
```

## 错误处理

### 前置条件检查失败
当前置条件检查失败时，测试用例将被跳过，并记录错误信息：

```
❌ 前置条件检查失败，跳过此测试用例
错误信息: 极光PDF未安装
```

### 软件启动失败
如果软件无法启动，会记录详细的错误信息：

```
❌ 前置条件失败: 无法启动极光PDF
错误信息: 启动软件 极光PDF 失败: 找不到可执行文件
```

## 配置选项

### 超时设置
- 软件启动等待时间：30秒
- 截图超时：10秒
- 元素等待超时：30秒

### 重试机制
- 步骤执行重试次数：3次
- 关键步骤失败时停止执行

## 日志记录

所有前置条件检查操作都会记录到日志文件中：

```
2025-08-14 10:58:48,192 - unified_automation_framework - INFO - 开始执行前置条件检查...
2025-08-14 10:58:48,193 - unified_automation_framework - INFO - 检查前置条件: 极光PDF已安装
2025-08-14 10:58:48,194 - unified_automation_framework - INFO - 软件 极光PDF 已安装在: C:\Program Files\JiGuangPDF
```

## 最佳实践

### 1. 测试用例设计
- 在描述中明确提及产品名称
- 使用标准的前置条件描述
- 避免过于复杂的前置条件

### 2. 环境准备
- 确保测试环境干净
- 预先安装必要的软件
- 准备测试数据文件

### 3. 错误处理
- 检查日志文件了解失败原因
- 验证软件安装状态
- 确认系统权限设置

## 故障排除

### 常见问题

1. **软件检测失败**
   - 检查软件是否已安装
   - 验证安装路径配置
   - 确认进程名称正确

2. **软件启动失败**
   - 检查可执行文件路径
   - 验证系统权限
   - 查看软件依赖

3. **窗口检测失败**
   - 确认窗口标题匹配
   - 检查窗口是否最小化
   - 验证窗口层级

### 调试模式

启用详细日志记录：

```python
import logging
logging.getLogger('unified_automation_framework').setLevel(logging.DEBUG)
```

## 扩展开发

### 添加新软件支持

1. 在`software_configs`中添加配置
2. 实现特定的检查逻辑
3. 添加相应的前置条件模板

### 自定义前置条件

1. 继承`TestCase`类
2. 重写`execute_preconditions`方法
3. 实现自定义检查逻辑

## 总结

前置条件检查功能大大提高了测试用例的可靠性和自动化程度。通过自动检测环境状态，避免了因环境问题导致的测试失败，提高了测试效率和质量。
