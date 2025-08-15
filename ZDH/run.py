#!/usr/bin/env python3
"""
Windows自动化测试系统 - 主启动脚本
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """主函数"""
    try:
        print("启动Windows自动化测试系统...")
        
        # 导入并启动服务
        from src.orchestrator.main import app
        import uvicorn
        
        # 启动服务
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8089,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"导入模块失败: {e}")
        print("请确保已安装所有依赖: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
