#!/usr/bin/env python3
"""
MCP服务器启动脚本
"""

import asyncio
import sys
import os
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import mcp
        print("✓ MCP库已安装")
    except ImportError:
        print("✗ MCP库未安装，请运行: pip install -r requirements.txt")
        return False
    
    try:
        import sqlite3
        print("✓ SQLite3已可用")
    except ImportError:
        print("✗ SQLite3不可用")
        return False
    
    return True

def main():
    """主函数"""
    print("=== MCP服务器启动器 ===")
    
    # 检查依赖
    if not check_dependencies():
        print("依赖检查失败，请安装所需依赖")
        sys.exit(1)
    
    # 检查服务器文件
    server_file = "simple_mcp_server.py"
    if not os.path.exists(server_file):
        print(f"✗ 服务器文件 {server_file} 不存在")
        sys.exit(1)
    
    print(f"✓ 找到服务器文件: {server_file}")
    
    # 启动服务器
    print("\n启动MCP服务器...")
    print("按 Ctrl+C 停止服务器")
    
    try:
        # 导入并运行服务器
        import subprocess
        process = subprocess.Popen([sys.executable, server_file])
        process.wait()
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"启动服务器时出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 