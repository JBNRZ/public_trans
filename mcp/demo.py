#!/usr/bin/env python3
"""
MCP应用演示脚本
展示如何使用MCP服务器
"""

import asyncio
import json
import subprocess
import sys
import time
from typing import Dict, Any

class MCPDemo:
    def __init__(self):
        self.process = None
        
    async def start_demo(self):
        """启动演示"""
        print("=== MCP应用演示 ===\n")
        
        print("1. 检查项目文件...")
        self.check_files()
        
        print("\n2. 安装依赖...")
        self.install_dependencies()
        
        print("\n3. 演示MCP服务器功能...")
        await self.demo_server_features()
        
        print("\n=== 演示完成 ===")
    
    def check_files(self):
        """检查项目文件"""
        files = [
            "simple_mcp_server.py",
            "requirements.txt", 
            "README.md",
            "config.json"
        ]
        
        for file in files:
            try:
                with open(file, 'r') as f:
                    print(f"✓ {file} - 存在")
            except FileNotFoundError:
                print(f"✗ {file} - 不存在")
    
    def install_dependencies(self):
        """安装依赖"""
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✓ 依赖安装成功")
            else:
                print("✗ 依赖安装失败")
                print(result.stderr)
        except Exception as e:
            print(f"✗ 安装依赖时出错: {e}")
    
    async def demo_server_features(self):
        """演示服务器功能"""
        print("\n启动MCP服务器进行演示...")
        
        # 启动服务器
        try:
            self.process = await asyncio.create_subprocess_exec(
                sys.executable, "simple_mcp_server.py",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # 等待服务器启动
            await asyncio.sleep(2)
            
            # 演示工具列表
            print("\n--- 演示工具列表 ---")
            await self.demo_list_tools()
            
            # 演示添加笔记
            print("\n--- 演示添加笔记 ---")
            await self.demo_add_note()
            
            # 演示列出笔记
            print("\n--- 演示列出笔记 ---")
            await self.demo_list_notes()
            
            # 演示获取时间
            print("\n--- 演示获取时间 ---")
            await self.demo_get_time()
            
        except Exception as e:
            print(f"演示过程中出错: {e}")
        finally:
            if self.process:
                self.process.terminate()
                await self.process.wait()
    
    async def send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """发送请求到MCP服务器"""
        if not self.process:
            return {"error": "服务器未启动"}
        
        try:
            request_str = json.dumps(request) + "\n"
            self.process.stdin.write(request_str.encode())
            await self.process.stdin.drain()
            
            response_line = await self.process.stdout.readline()
            response = json.loads(response_line.decode().strip())
            return response
        except Exception as e:
            return {"error": f"请求失败: {e}"}
    
    async def demo_list_tools(self):
        """演示工具列表"""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        response = await self.send_request(request)
        print(f"可用工具: {json.dumps(response, indent=2, ensure_ascii=False)}")
    
    async def demo_add_note(self):
        """演示添加笔记"""
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "add_note",
                "arguments": {
                    "title": "演示笔记",
                    "content": "这是一个通过MCP协议添加的演示笔记"
                }
            }
        }
        
        response = await self.send_request(request)
        print(f"添加笔记结果: {json.dumps(response, indent=2, ensure_ascii=False)}")
    
    async def demo_list_notes(self):
        """演示列出笔记"""
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "list_notes",
                "arguments": {}
            }
        }
        
        response = await self.send_request(request)
        print(f"笔记列表: {json.dumps(response, indent=2, ensure_ascii=False)}")
    
    async def demo_get_time(self):
        """演示获取时间"""
        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "get_time",
                "arguments": {}
            }
        }
        
        response = await self.send_request(request)
        print(f"时间信息: {json.dumps(response, indent=2, ensure_ascii=False)}")

def main():
    """主函数"""
    demo = MCPDemo()
    asyncio.run(demo.start_demo())

if __name__ == "__main__":
    main() 