#!/usr/bin/env python3
"""
简单的MCP服务器应用
"""

import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import CallToolResult, ListToolsResult, Tool

# 创建MCP服务器实例
server = Server("simple-mcp-server")

# 存储数据
notes = []

@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """列出可用的工具"""
    tools = [
        Tool(
            name="add_note",
            description="添加一个新的笔记",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "笔记标题"},
                    "content": {"type": "string", "description": "笔记内容"}
                },
                "required": ["title", "content"]
            }
        ),
        Tool(
            name="list_notes",
            description="列出所有笔记",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_time",
            description="获取当前时间",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]
    return ListToolsResult(tools=tools)

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """处理工具调用"""
    try:
        if name == "add_note":
            return await add_note(arguments)
        elif name == "list_notes":
            return await list_notes(arguments)
        elif name == "get_time":
            return await get_time(arguments)
        else:
            return CallToolResult(
                content=[{"type": "text", "text": f"未知工具: {name}"}],
                isError=True
            )
    except Exception as e:
        return CallToolResult(
            content=[{"type": "text", "text": f"工具调用失败: {str(e)}"}],
            isError=True
        )

async def add_note(arguments: Dict[str, Any]) -> CallToolResult:
    """添加笔记"""
    title = arguments.get("title", "")
    content = arguments.get("content", "")
    
    note = {
        "id": len(notes) + 1,
        "title": title,
        "content": content,
        "created_at": datetime.now().isoformat()
    }
    
    notes.append(note)
    
    return CallToolResult(
        content=[{
            "type": "text",
            "text": f"笔记已添加: {title}\nID: {note['id']}"
        }]
    )

async def list_notes(arguments: Dict[str, Any]) -> CallToolResult:
    """列出笔记"""
    if not notes:
        return CallToolResult(
            content=[{"type": "text", "text": "暂无笔记"}]
        )
    
    result = "笔记列表:\n\n"
    for note in notes:
        result += f"ID: {note['id']}\n"
        result += f"标题: {note['title']}\n"
        result += f"内容: {note['content']}\n"
        result += f"创建时间: {note['created_at']}\n"
        result += "-" * 30 + "\n"
    
    return CallToolResult(
        content=[{"type": "text", "text": result}]
    )

async def get_time(arguments: Dict[str, Any]) -> CallToolResult:
    """获取当前时间"""
    now = datetime.now()
    time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    
    return CallToolResult(
        content=[{"type": "text", "text": f"当前时间: {time_str}"}]
    )

async def main():
    """主函数"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="simple-mcp-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main()) 