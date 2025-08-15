# 🧪 ZDH - 智能自动化测试系统

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/Platform-Windows-green.svg)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 项目概述

ZDH是一个基于AI的Windows平台智能自动化测试系统，专门设计用于测试使用贝壳库（纯画图界面）的C++客户端应用程序。系统集成了OCR识别、UI自动化、AI驱动测试用例生成、智能前置条件执行等核心功能，能够从自然语言或流程图输入自动生成完整的测试用例集。

## 🎯 核心特性

### 🤖 AI驱动测试
- **智能测试用例生成**: 使用Claude 4从自然语言描述自动生成测试用例
- **AI前置条件执行**: 自动识别并执行测试前置条件（如启动软件、打开文件等）
- **智能错误诊断**: AI辅助分析和解决测试执行中的问题

### 🔧 多维度自动化
- **文件操作自动化**: 智能定位和打开桌面文件
- **应用程序自动化**: 启动、操作、验证各种Windows应用程序
- **网页自动化**: 浏览器操作、页面导航、内容验证
- **UI界面自动化**: 支持纯画图界面的图像识别和操作

### 📊 完整的测试生态
- **测试用例管理**: 支持CSV导入、JSON转换、批量执行
- **详细测试报告**: 自动生成包含截图、日志、性能指标的测试报告
- **配置管理**: 灵活的配置文件和环境变量管理
- **错误处理**: 完善的异常处理和重试机制

## 🏗️ 系统架构

```
ZDH/
├── src/                           # 核心源代码
│   ├── ai_interface/             # AI接口层
│   ├── orchestrator/             # 协调器层
│   ├── ui_automation/            # UI自动化层
│   ├── utils/                    # 工具类
│   └── data_store/               # 数据存储层
├── config/                       # 配置文件
├── data/                         # 数据目录
│   ├── logs/                     # 日志文件
│   ├── reports/                  # 测试报告
│   ├── screenshots/              # 截图存储
│   └── templates/                # 模板文件
├── tests/                        # 测试文件
├── docs/                         # 文档目录
└── requirements.txt              # 依赖包列表
```

## 🚀 快速开始

### 1. 环境要求

- **操作系统**: Windows 7/8/10/11 (32位/64位)
- **Python版本**: 3.11+
- **硬件要求**: 8GB+ RAM, 4核+ CPU
- **权限要求**: 管理员权限（用于UI自动化）

### 2. GitHub导入（可选）

如果您想将项目导入到GitHub，我们提供了多种便捷方式：

```bash
# 方案1: 批处理文件（推荐Windows用户）
setup_github.bat

# 方案2: PowerShell脚本（推荐PowerShell用户）
.\setup_github.ps1

# 方案3: Python脚本（推荐Python用户）
python setup_github.py

# 方案4: 手动执行（推荐高级用户）
# 参考 GITHUB_IMPORT_GUIDE.md
```

详细说明请参考：[快速导入指南](QUICK_GITHUB_IMPORT.md)

### 3. 安装依赖

```bash
# 克隆项目
git clone <your-repo-url>
cd ZDH

# 安装Python依赖
pip install -r requirements.txt

# 或者安装最小依赖版本
pip install -r requirements_minimal.txt
```

### 4. 配置系统

```bash
# 复制环境变量配置文件
copy env.example .env

# 编辑.env文件，配置必要的环境变量
# 特别是CLAUDE_API_KEY（用于AI功能）
```

### 5. 运行演示

```bash
# 运行框架演示
python framework_demo.py

# 运行Edge浏览器自动化测试
python edge_baidu_automation.py

# 运行文件打开测试
python auto_file_opener.py
```

## 📚 核心组件详解

### 1. 统一自动化框架 (unified_automation_framework.py)

**功能**: 整个系统的核心框架，集成所有自动化功能

**主要特性**:
- 支持多种操作类型（文件、应用、网页、UI操作）
- AI前置条件自动执行
- 智能错误处理和重试机制
- 自动截图和日志记录
- 详细的测试报告生成

**核心方法**:
```python
from unified_automation_framework import UnifiedAutomationFramework

# 创建框架实例
framework = UnifiedAutomationFramework()

# 执行测试用例
result = framework.execute_test_case(test_case)

# 批量执行测试
results = framework.execute_batch_tests(test_cases)
```

### 2. AI前置条件执行系统

**功能**: 智能识别和执行测试前置条件

**支持的前置条件**:
- 软件安装检查
- 应用程序启动
- 文件打开操作
- 文本选择操作
- 右键菜单操作

**示例**:
```python
# 自动执行前置条件
preconditions = [
    "打开PDF阅读器界面",
    "打开文件选取一段文字",
    "右键点击选取文字区域"
]

for precondition in preconditions:
    framework.execute_precondition(precondition)
```

### 3. OCR图像识别系统 (optimized_ocr_system.py)

**功能**: 基于EasyOCR的智能图像识别

**主要特性**:
- 多语言支持（中文、英文）
- 图像预处理优化
- 智能文本定位
- 置信度阈值控制

**核心方法**:
```python
from optimized_ocr_system import OptimizedOCRSystem

ocr = OptimizedOCRSystem()

# 识别屏幕文本
text_results = ocr.recognize_text(screenshot)

# 查找特定文本
text_positions = ocr.find_text_positions("目标文本")
```

### 4. 测试用例转换器 (csv_to_automation_converter.py)

**功能**: 将CSV格式的测试用例转换为可执行的自动化测试

**支持格式**:
- CSV导入
- JSON输出
- 批量转换
- 格式验证

**使用方法**:
```python
from csv_to_automation_converter import CSVAutomationConverter

converter = CSVAutomationConverter()
converted_cases = converter.convert_csv_to_test_cases("test_cases.csv")
```

## 🔧 配置管理

### 1. 环境变量配置 (.env)

```bash
# AI接口配置
CLAUDE_API_KEY=your_claude_api_key
CLAUDE_API_URL=https://api.anthropic.com

# 系统配置
LOG_LEVEL=INFO
SCREENSHOT_ENABLED=true
RETRY_COUNT=3

# 路径配置
DATA_DIR=./data
REPORTS_DIR=./reports
SCREENSHOTS_DIR=./screenshots
```

### 2. 测试配置 (test_case_config.json)

```json
{
  "test_case": {
    "name": "示例测试用例",
    "description": "测试用例描述",
    "timeout": 30,
    "retry_count": 3
  },
  "ocr_settings": {
    "confidence_threshold": 0.3,
    "languages": ["ch_sim", "en"],
    "image_preprocessing": true
  },
  "automation_settings": {
    "click_interval": 0.5,
    "search_delay": 1.0,
    "failsafe_enabled": true
  }
}
```

## 📊 测试报告系统

### 1. 报告内容

- **执行摘要**: 测试用例执行状态和统计
- **步骤详情**: 每个步骤的执行结果和截图
- **性能指标**: 执行时间、OCR时间、定位时间
- **错误信息**: 详细的错误日志和堆栈跟踪
- **改进建议**: AI生成的优化建议

### 2. 报告格式

```json
{
  "test_case_id": "TC001",
  "execution_time": "2025-08-14T10:30:00",
  "status": "PASS",
  "total_duration": 15.5,
  "steps": [
    {
      "step_id": "step_1",
      "description": "打开应用程序",
      "status": "PASS",
      "duration": 2.3,
      "screenshot": "step_1_screenshot.png"
    }
  ],
  "performance_metrics": {
    "ocr_time": 1.2,
    "location_time": 0.8,
    "execution_time": 13.5
  }
}
```

## 🎯 使用场景

### 1. 软件测试自动化

```python
# 测试PDF阅读器功能
test_case = TestCase(
    name="PDF阅读器测试",
    description="测试PDF文件的打开、阅读、标注功能",
    steps=[
        AutomationStep("打开PDF", ActionType.OPEN_FILE, {"file": "test.pdf"}),
        AutomationStep("选择文本", ActionType.CLICK, {"text": "示例文本"}),
        AutomationStep("添加标注", ActionType.CLICK, {"button": "标注按钮"})
    ]
)
```

### 2. 网页自动化测试

```python
# 测试网站功能
test_case = TestCase(
    name="网站导航测试",
    description="测试网站的基本导航功能",
    steps=[
        AutomationStep("打开浏览器", ActionType.OPEN_APPLICATION, {"app": "edge"}),
        AutomationStep("访问网站", ActionType.NAVIGATE_URL, {"url": "https://www.baidu.com"}),
        AutomationStep("搜索内容", ActionType.TYPE, {"text": "测试内容"})
    ]
)
```

### 3. 文件操作自动化

```python
# 测试文件操作
test_case = TestCase(
    name="文件操作测试",
    description="测试文件的打开、编辑、保存功能",
    steps=[
        AutomationStep("打开文件", ActionType.OPEN_FILE, {"file": "info.json"}),
        AutomationStep("编辑内容", ActionType.TYPE, {"text": "新内容"}),
        AutomationStep("保存文件", ActionType.PRESS_KEY, {"key": "ctrl+s"})
    ]
)
```

## 🔍 故障排除

### 常见问题

1. **OCR识别失败**
   ```bash
   # 检查EasyOCR安装
   pip install easyocr
   
   # 调整置信度阈值
   # 在配置文件中设置 confidence_threshold: 0.2
   ```

2. **UI自动化权限问题**
   ```bash
   # 以管理员身份运行
   # 确保应用程序有足够的权限
   ```

3. **AI接口连接失败**
   ```bash
   # 检查API密钥配置
   # 验证网络连接
   # 确认API配额
   ```

### 调试模式

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 启用详细日志
framework = UnifiedAutomationFramework(debug=True)
```

## 📈 性能优化

### 1. OCR优化

- **图像预处理**: 1.5倍放大、对比度增强1.3倍、锐度增强1.3倍
- **多语言支持**: 中文简体 + 英文
- **置信度阈值**: 0.3（平衡精度和召回率）

### 2. 自动化优化

- **智能延迟**: 点击间隔0.5秒，搜索延迟1.0秒
- **故障安全**: 启用pyautogui的failsafe机制
- **重试机制**: 最多重试3次

### 3. 内存优化

- **截图压缩**: 自动压缩大尺寸截图
- **日志轮转**: 定期清理旧日志文件
- **缓存管理**: 智能缓存OCR结果

## 🚀 扩展开发

### 1. 添加新的操作类型

```python
class ActionType(Enum):
    # 现有类型
    OPEN_FILE = "open_file"
    CLICK = "click"
    
    # 新增类型
    CUSTOM_ACTION = "custom_action"

# 实现对应的处理方法
def _execute_custom_action(self, step: AutomationStep):
    # 自定义操作逻辑
    pass
```

### 2. 集成新的AI模型

```python
class CustomAIModel:
    def __init__(self, model_config):
        self.model = load_model(model_config)
    
    def analyze_test_case(self, description):
        # 自定义AI分析逻辑
        return test_case
```

### 3. 支持新的文件格式

```python
class CustomFileHandler:
    def __init__(self):
        self.supported_formats = ['.custom']
    
    def open_file(self, file_path):
        # 自定义文件打开逻辑
        pass
```

## 📚 相关文档

- [技术设计文档](technical_design.md) - 详细的系统架构设计
- [框架使用指南](FRAMEWORK_GUIDE.md) - 框架的详细使用方法
- [快速开始指南](QUICKSTART.md) - 快速上手指南
- [AI前置条件执行指南](AI_PRECONDITION_EXECUTION_GUIDE.md) - AI功能使用说明
- [测试执行总结](TEST_EXECUTION_SUMMARY.md) - 测试执行相关说明

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 技术支持

如遇到问题，请：

1. 查看 [故障排除](#故障排除) 部分
2. 检查日志文件 (`data/logs/`)
3. 运行系统测试 (`python test_system.py`)
4. 提交 Issue 并附上详细的错误信息

## 🎉 总结

ZDH智能自动化测试系统提供了一个完整的解决方案，通过AI驱动、多维度自动化、完整的测试生态等特性，能够：

- 🚀 **快速生成测试用例**: 从自然语言描述自动生成完整测试用例
- 🤖 **智能执行前置条件**: AI自动识别并执行测试前置条件
- 🔧 **多维度自动化**: 支持文件、应用、网页、UI等多种操作
- 📊 **完整测试报告**: 自动生成详细的测试报告和性能分析
- 🛠️ **高度可扩展**: 模块化设计，易于扩展和维护

系统设计灵活，易于扩展，可以作为企业级自动化测试的基础框架，大幅提升测试效率和质量。
