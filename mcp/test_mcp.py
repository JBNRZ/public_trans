#!/usr/bin/env python3
"""
MCP服务器测试脚本
"""

import asyncio
import json
import subprocess
import sys
from typing import Dict, Any

class MCPTester:
    def __init__(self):
        self.process = None
        
    async def start_server(self):
        """启动MCP服务器"""
        try:
            self.process = await asyncio.create_subprocess_exec(
                sys.executable, "simple_mcp_server.py",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            print("MCP服务器已启动")
        except Exception as e:
            print(f"启动服务器失败: {e}")
            return False
        return True
    
    async def send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """发送请求到MCP服务器"""
        if not self.process:
            return {"error": "服务器未启动"}
        
        try:
            # 发送请求
            request_str = json.dumps(request) + "\n"
            self.process.stdin.write(request_str.encode())
            await self.process.stdin.drain()
            
            # 读取响应
            response_line = await self.process.stdout.readline()
            response = json.loads(response_line.decode().strip())
            return response
        except Exception as e:
            return {"error": f"请求失败: {e}"}
    
    async def test_tools(self):
        """测试工具功能"""
        print("\n=== 测试工具功能 ===")
        
        # 测试获取时间
        print("\n1. 测试获取时间:")
        time_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "get_time",
                "arguments": {}
            }
        }
        response = await self.send_request(time_request)
        print(f"响应: {json.dumps(response, indent=2, ensure_ascii=False)}")
        
        # 测试添加笔记
        print("\n2. 测试添加笔记:")
        add_note_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "add_note",
                "arguments": {
                    "title": "测试笔记",
                    "content": "这是一个测试笔记的内容"
                }
            }
        }
        response = await self.send_request(add_note_request)
        print(f"响应: {json.dumps(response, indent=2, ensure_ascii=False)}")
        
        # 测试列出笔记
        print("\n3. 测试列出笔记:")
        list_notes_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "list_notes",
                "arguments": {}
            }
        }
        response = await self.send_request(list_notes_request)
        print(f"响应: {json.dumps(response, indent=2, ensure_ascii=False)}")
    
    async def test_list_tools(self):
        """测试工具列表功能"""
        print("\n=== 测试工具列表 ===")
        
        list_tools_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/list",
            "params": {}
        }
        response = await self.send_request(list_tools_request)
        print(f"可用工具: {json.dumps(response, indent=2, ensure_ascii=False)}")
    
    async def cleanup(self):
        """清理资源"""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            print("MCP服务器已停止")

async def main():
    """主测试函数"""
    tester = MCPTester()
    
    try:
        # 启动服务器
        if not await tester.start_server():
            return
        
        # 等待服务器启动
        await asyncio.sleep(1)
        
        # 测试工具列表
        await tester.test_list_tools()
        
        # 测试工具功能
        await tester.test_tools()
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    print("开始测试MCP服务器...")
    asyncio.run(main())
    print("测试完成!") 