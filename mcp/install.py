#!/usr/bin/env python3
"""
MCP应用安装脚本
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("✗ 需要Python 3.8或更高版本")
        return False
    print(f"✓ Python版本: {sys.version}")
    return True

def install_dependencies():
    """安装依赖"""
    print("\n正在安装依赖...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ 依赖安装成功")
            return True
        else:
            print("✗ 依赖安装失败")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"✗ 安装依赖时出错: {e}")
        return False

def create_directories():
    """创建必要的目录"""
    directories = ["data", "logs", "config"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ 创建目录: {directory}")

def check_files():
    """检查必要文件"""
    required_files = [
        "simple_mcp_server.py",
        "requirements.txt",
        "README.md",
        "config.json"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
        else:
            print(f"✓ 文件存在: {file}")
    
    if missing_files:
        print(f"✗ 缺少文件: {missing_files}")
        return False
    
    return True

def test_imports():
    """测试导入"""
    try:
        import mcp
        print("✓ MCP库导入成功")
    except ImportError:
        print("✗ MCP库导入失败")
        return False
    
    try:
        import sqlite3
        print("✓ SQLite3导入成功")
    except ImportError:
        print("✗ SQLite3导入失败")
        return False
    
    return True

def create_sample_data():
    """创建示例数据"""
    sample_config = {
        "server": {
            "name": "mcp-demo-server",
            "version": "1.0.0",
            "description": "MCP演示服务器"
        },
        "database": {
            "type": "sqlite",
            "path": "data/mcp_data.db"
        },
        "logging": {
            "level": "INFO",
            "file": "logs/mcp_server.log"
        }
    }
    
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(sample_config, f, indent=2, ensure_ascii=False)
    
    print("✓ 配置文件已创建")

def main():
    """主安装函数"""
    print("=== MCP应用安装程序 ===\n")
    
    # 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 检查文件
    if not check_files():
        print("请确保所有必要文件都存在")
        sys.exit(1)
    
    # 创建目录
    create_directories()
    
    # 安装依赖
    if not install_dependencies():
        print("依赖安装失败，请手动安装")
        sys.exit(1)
    
    # 测试导入
    if not test_imports():
        print("导入测试失败")
        sys.exit(1)
    
    # 创建示例配置
    create_sample_data()
    
    print("\n=== 安装完成 ===")
    print("\n下一步:")
    print("1. 运行演示: python demo.py")
    print("2. 启动服务器: python simple_mcp_server.py")
    print("3. 查看文档: README.md")

if __name__ == "__main__":
    main() 