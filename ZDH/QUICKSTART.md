# Windows自动化测试系统 - 快速开始指南

## 系统概述

这是一个基于AI的Windows平台自动化测试系统，专门设计用于测试使用贝壳库（纯画图界面）的C++客户端应用程序。系统能够从自然语言或流程图输入自动生成完整的测试用例集。

## 核心特性

- **AI驱动**: 使用Claude 4进行智能分析和测试用例生成
- **自然语言输入**: 支持自然语言描述和流程图输入，无需维护脚本
- **贝壳库支持**: 专门针对纯画图界面的UI自动化解决方案
- **全面覆盖**: 自动生成覆盖主流程、分支、异常、边界条件的测试用例

## 快速开始

### 1. 环境要求

- Windows 7/8/10/11 (32位/64位)
- Python 3.11+
- 8GB+ RAM, 4核+ CPU
- 管理员权限

### 2. 安装依赖

```bash
# 克隆项目
git clone <your-repo-url>
cd ZDH

# 安装Python依赖
pip install -r requirements.txt
```

### 3. 配置系统

```bash
# 复制环境变量配置文件
copy env.example .env

# 编辑.env文件，配置必要的环境变量
# 特别是CLAUDE_API_KEY
```

### 4. 测试系统

```bash
# 运行系统测试
python test_system.py
```

### 5. 启动服务

```bash
# 启动主服务
python run.py
```

服务将在 `http://127.0.0.1:8089` 启动

## API接口使用

### 1. 业务流程分析

```bash
curl -X POST "http://127.0.0.1:8089/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "input_type": "natural_language",
    "content": "用户启动贝壳库应用，进行核心功能操作，查看操作结果，验证功能正确性",
    "context": {
      "application": "贝壳库应用",
      "version": "最新版本",
      "interface_type": "贝壳库纯画图界面"
    }
  }'
```

### 2. 测试用例生成

```bash
curl -X POST "http://127.0.0.1:8089/api/v1/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "business_model": {
      "name": "示例业务流程",
      "nodes": [...],
      "flows": [...]
    },
    "coverage_requirements": {
      "main_flow": true,
      "branch_flow": true,
      "exception_flow": true,
      "boundary_conditions": true
    }
  }'
```

### 3. 测试用例执行

```bash
curl -X POST "http://127.0.0.1:8089/api/v1/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "test_case_id": "test_case_001",
    "environment": "sandbox",
    "beike_ui_config": {
      "image_recognition": true,
      "coordinate_fallback": true,
      "ocr_enabled": true
    }
  }'
```

## 贝壳库UI自动化

### 1. 界面识别策略

系统采用多层级识别策略：

1. **图像识别**: 使用OpenCV进行模板匹配
2. **坐标定位**: 基于缓存的坐标信息
3. **颜色匹配**: 通过颜色模式识别元素
4. **OCR文本**: 识别界面中的文本内容

### 2. 配置界面识别

在 `config/config.yaml` 中配置贝壳库UI相关设置：

```yaml
beike_ui:
  recognition_priority:
    - "image_recognition"
    - "coordinate_positioning"
    - "color_matching"
    - "ocr_text"
  
  coordinate_cache:
    enabled: true
    auto_update: true
    validation_interval: 300
```

### 3. 添加图像模板

```python
from src.ui_automation.beike_ui_locator import BeikeUILocator

locator = BeikeUILocator()
locator.add_image_template("start_button", "templates/start_button.png")
```

## 测试用例设计

### 1. 自然语言输入示例

```
"用户启动贝壳库应用，点击主界面上的扫描按钮，等待扫描完成，验证扫描结果显示正确"
```

### 2. 流程图输入示例

```
[启动应用] -> [等待主界面] -> [点击扫描按钮] -> [等待扫描] -> [验证结果]
```

### 3. 测试用例结构

```json
{
  "id": "test_case_001",
  "name": "基础功能测试",
  "description": "测试应用的基本功能",
  "priority": "high",
  "category": "functional",
  "preconditions": ["启动应用: C:\\App\\app.exe"],
  "test_steps": [
    {
      "step_id": "1",
      "action": "click",
      "target": "scan_button",
      "expected_result": "扫描开始"
    }
  ],
  "postconditions": ["关闭应用"]
}
```

## 监控和管理

### 1. 健康检查

```bash
curl "http://127.0.0.1:8089/health"
```

### 2. 执行状态查询

```bash
curl "http://127.0.0.1:8089/api/v1/execute/summary"
```

### 3. 导出测试报告

```bash
curl "http://127.0.0.1:8089/api/v1/execute/{execution_id}/report?format=json"
```

## 故障排除

### 1. 常见问题

**问题**: 配置加载失败
**解决**: 检查 `config/config.yaml` 文件是否存在且格式正确

**问题**: Claude API连接失败
**解决**: 检查 `.env` 文件中的 `CLAUDE_API_KEY` 是否正确

**问题**: UI自动化失败
**解决**: 检查目标应用是否正在运行，界面元素是否可见

### 2. 日志查看

日志文件位置：`data/logs/test_system.log`

### 3. 调试模式

设置日志级别为DEBUG：

```yaml
logging:
  level: "DEBUG"
```

## 扩展开发

### 1. 添加新的UI操作

在 `src/ui_automation/ui_executor.py` 中添加新的操作方法

### 2. 自定义AI提示词

在 `src/ai_interface/claude_client.py` 中修改提示词模板

### 3. 集成新的测试框架

在 `src/orchestrator/test_executor.py` 中扩展测试执行逻辑

## 安全注意事项

- 所有测试操作都应在隔离的沙箱环境中进行
- 不要在生产环境中使用此系统
- 高危操作需要人工确认
- 定期审查审计日志

## 获取帮助

- 查看完整文档：`docs/` 目录
- 检查配置示例：`config/config.yaml`
- 运行系统测试：`python test_system.py`
- 查看API文档：启动服务后访问 `http://127.0.0.1:8089/docs`

---

**注意**: 本系统专门设计用于测试环境，请勿在生产环境中使用。
