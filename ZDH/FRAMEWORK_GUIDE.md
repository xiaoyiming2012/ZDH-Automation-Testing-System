# 统一自动化测试框架使用指南

## 概述

统一自动化测试框架是一个集成了文件打开、应用程序启动、网页自动化等功能的综合测试框架。它将之前开发的各个独立功能整合到一个统一的架构中，提供了更好的可维护性和扩展性。

## 框架特点

- ✅ **统一管理**: 所有自动化功能集成在一个框架中
- ✅ **多种操作类型**: 支持文件、应用程序、网页等多种操作
- ✅ **自动截图**: 每个步骤自动截图记录
- ✅ **详细日志**: 完整的执行日志记录
- ✅ **测试报告**: 自动生成详细的测试报告
- ✅ **配置管理**: 灵活的配置文件管理
- ✅ **错误处理**: 完善的错误处理和重试机制

## 快速开始

### 1. 安装依赖

确保已安装所有必要的Python包：

```bash
pip install pyautogui pywinauto psutil easyocr opencv-python pillow
```

### 2. 运行演示

```bash
python framework_demo.py
```

这将运行完整的演示，包括：
- 文件打开测试
- 应用程序启动测试
- 网页导航测试
- 自定义测试用例
- 批量执行测试

### 3. 基本使用

```python
from unified_automation_framework import UnifiedAutomationFramework

# 创建框架实例
framework = UnifiedAutomationFramework()

# 创建文件打开测试
test_case = framework.create_file_opening_test("info.json")

# 执行测试
result = framework.execute_test_case(test_case)

# 查看结果
print(f"测试结果: {result['status']}")
```

## 核心组件

### 1. ActionType 枚举

定义了支持的操作类型：

```python
class ActionType(Enum):
    OPEN_FILE = "open_file"           # 打开文件
    OPEN_APPLICATION = "open_application"  # 打开应用程序
    CLICK = "click"                   # 点击操作
    TYPE = "type"                     # 输入文本
    PRESS_KEY = "press_key"           # 按键操作
    WAIT = "wait"                     # 等待操作
    SCREENSHOT = "screenshot"         # 截图操作
    VERIFY = "verify"                 # 验证操作
    NAVIGATE_URL = "navigate_url"     # 网页导航
```

### 2. AutomationStep 数据类

定义单个自动化步骤：

```python
@dataclass
class AutomationStep:
    step_id: str                      # 步骤ID
    action_type: ActionType           # 操作类型
    description: str                  # 步骤描述
    parameters: Dict[str, Any]        # 操作参数
    expected_result: str              # 期望结果
    timeout: int = 30                 # 超时时间
    retry_count: int = 3              # 重试次数
    critical: bool = True             # 是否关键步骤
```

### 3. TestCase 数据类

定义完整的测试用例：

```python
@dataclass
class TestCase:
    case_id: str                      # 用例ID
    name: str                         # 用例名称
    description: str                  # 用例描述
    steps: List[AutomationStep]       # 步骤列表
    preconditions: List[str] = None   # 前置条件
    postconditions: List[str] = None  # 后置条件
    tags: List[str] = None            # 标签
```

## 使用示例

### 1. 文件打开测试

```python
# 创建文件打开测试用例
test_case = framework.create_file_opening_test("info.json")

# 执行测试
result = framework.execute_test_case(test_case)
```

### 2. 应用程序启动测试

```python
# 创建应用程序启动测试用例
test_case = framework.create_application_opening_test("github_desktop")

# 执行测试
result = framework.execute_test_case(test_case)
```

### 3. 网页导航测试

```python
# 创建网页导航测试用例
test_case = framework.create_web_navigation_test("www.baidu.com", "访问百度网站")

# 执行测试
result = framework.execute_test_case(test_case)
```

### 4. 自定义测试用例

```python
from unified_automation_framework import TestCase, AutomationStep, ActionType

# 创建自定义步骤
steps = [
    AutomationStep(
        step_id="step_001",
        action_type=ActionType.OPEN_FILE,
        description="打开文件",
        parameters={"filename": "info.json"},
        expected_result="文件成功打开"
    ),
    AutomationStep(
        step_id="step_002",
        action_type=ActionType.WAIT,
        description="等待文件打开",
        parameters={"time": 3},
        expected_result="等待完成"
    ),
    AutomationStep(
        step_id="step_003",
        action_type=ActionType.SCREENSHOT,
        description="截图验证",
        parameters={"filename": "verification.png"},
        expected_result="成功截图"
    )
]

# 创建测试用例
test_case = TestCase(
    case_id="custom_test",
    name="自定义测试",
    description="自定义测试用例示例",
    steps=steps
)

# 执行测试
result = framework.execute_test_case(test_case)
```

### 5. 批量执行测试

```python
# 创建多个测试用例
test_cases = [
    framework.create_file_opening_test("info.json"),
    framework.create_application_opening_test("github_desktop"),
    framework.create_web_navigation_test("www.baidu.com")
]

# 批量执行
results = []
for test_case in test_cases:
    result = framework.execute_test_case(test_case)
    results.append(result)

# 生成报告
report_path = framework.generate_report(results)
```

## 配置管理

框架使用JSON配置文件管理各种设置。默认配置文件为 `test_case_config.json`：

```json
{
    "ocr": {
        "enabled": true,
        "language": "ch_sim+en",
        "confidence": 0.6
    },
    "image_recognition": {
        "confidence": 0.8,
        "cache_enabled": true
    },
    "ui_automation": {
        "default_timeout": 30,
        "retry_count": 3,
        "click_delay": 0.5
    },
    "file_operations": {
        "desktop_path": "~/Desktop",
        "common_paths": [
            "~/Desktop",
            "~/Documents",
            "~/Downloads"
        ]
    },
    "applications": {
        "edge": {
            "paths": [
                "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
                "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe"
            ],
            "process_name": "msedge.exe"
        },
        "github_desktop": {
            "paths": [
                "C:\\Users\\{username}\\AppData\\Local\\GitHubDesktop\\GitHubDesktop.exe"
            ],
            "process_name": "GitHubDesktop.exe"
        }
    }
}
```

## 输出文件

框架运行后会生成以下文件：

### 1. 截图文件
- 位置: `screenshots/` 目录
- 格式: PNG
- 命名: `before_step_id.png`, `after_step_id.png`

### 2. 测试报告
- 位置: `reports/` 目录
- 格式: JSON
- 命名: `test_report_YYYYMMDD_HHMMSS.json`

### 3. 日志文件
- 位置: `automation_framework.log`
- 格式: 文本
- 内容: 详细的执行日志

## 错误处理

框架提供了完善的错误处理机制：

1. **步骤级错误处理**: 每个步骤都有独立的错误处理
2. **重试机制**: 可配置的重试次数
3. **关键步骤控制**: 关键步骤失败时停止执行
4. **详细错误信息**: 记录详细的错误信息和堆栈跟踪

## 扩展开发

### 添加新的操作类型

1. 在 `ActionType` 枚举中添加新类型
2. 在 `execute_step` 方法中添加对应的处理逻辑
3. 更新配置文件和文档

### 添加新的应用程序支持

1. 在配置文件的 `applications` 部分添加新应用
2. 提供正确的路径和进程名
3. 测试验证

## 最佳实践

1. **测试用例设计**: 将复杂的测试分解为多个简单步骤
2. **错误处理**: 合理设置关键步骤和重试次数
3. **截图管理**: 定期清理截图文件以节省空间
4. **配置管理**: 使用配置文件管理环境相关的设置
5. **日志分析**: 定期分析日志文件以优化测试流程

## 故障排除

### 常见问题

1. **OCR识别失败**: 检查OCR配置和语言设置
2. **文件未找到**: 检查文件路径配置
3. **应用程序启动失败**: 检查应用程序路径和进程名
4. **截图失败**: 检查截图目录权限

### 调试技巧

1. 启用详细日志输出
2. 检查生成的截图文件
3. 查看测试报告中的错误信息
4. 使用较小的超时时间进行快速测试

## 总结

统一自动化测试框架提供了一个完整的解决方案，将之前开发的各个功能整合到一个统一的架构中。通过使用这个框架，您可以：

- 快速创建和执行各种自动化测试
- 获得详细的执行报告和日志
- 灵活配置和管理测试环境
- 轻松扩展新的功能

框架的设计遵循了模块化和可扩展的原则，可以满足各种自动化测试需求。
