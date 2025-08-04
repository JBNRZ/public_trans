#!/usr/bin/env python3
"""
MCP (Model Context Protocol) 服务器应用
提供基本的工具和资源功能
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence
from pathlib import Path

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    ReadResourceRequest,
    ReadResourceResult,
    Resource,
    Tool,
    WriteResourceRequest,
    WriteResourceResult,
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建MCP服务器实例
server = Server("mcp-demo-server")

# 存储简单的数据
data_store = {
    "notes": [],
    "tasks": [],
    "config": {}
}

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
                    "content": {"type": "string", "description": "笔记内容"},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "标签列表"}
                },
                "required": ["title", "content"]
            }
        ),
        Tool(
            name="list_notes",
            description="列出所有笔记",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "返回的笔记数量限制"}
                }
            }
        ),
        Tool(
            name="get_time",
            description="获取当前时间",
            inputSchema={
                "type": "object",
                "properties": {
                    "format": {"type": "string", "description": "时间格式 (可选)"}
                }
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
        logger.error(f"工具调用错误: {e}")
        return CallToolResult(
            content=[{"type": "text", "text": f"工具调用失败: {str(e)}"}],
            isError=True
        )

async def add_note(arguments: Dict[str, Any]) -> CallToolResult:
    """添加笔记"""
    title = arguments.get("title", "")
    content = arguments.get("content", "")
    tags = arguments.get("tags", [])
    
    note = {
        "id": len(data_store["notes"]) + 1,
        "title": title,
        "content": content,
        "tags": tags,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    data_store["notes"].append(note)
    
    return CallToolResult(
        content=[{
            "type": "text",
            "text": f"笔记已添加: {title}\nID: {note['id']}\n内容: {content[:100]}{'...' if len(content) > 100 else ''}"
        }]
    )

async def list_notes(arguments: Dict[str, Any]) -> CallToolResult:
    """列出笔记"""
    limit = arguments.get("limit", 10)
    notes = data_store["notes"][-limit:] if limit > 0 else data_store["notes"]
    
    if not notes:
        return CallToolResult(
            content=[{"type": "text", "text": "暂无笔记"}]
        )
    
    result = "笔记列表:\n\n"
    for note in notes:
        result += f"ID: {note['id']}\n"
        result += f"标题: {note['title']}\n"
        result += f"内容: {note['content'][:100]}{'...' if len(note['content']) > 100 else ''}\n"
        result += f"标签: {', '.join(note['tags']) if note['tags'] else '无'}\n"
        result += f"创建时间: {note['created_at']}\n"
        result += "-" * 50 + "\n"
    
    return CallToolResult(
        content=[{"type": "text", "text": result}]
    )

async def get_time(arguments: Dict[str, Any]) -> CallToolResult:
    """获取当前时间"""
    time_format = arguments.get("format", "default")
    now = datetime.now()
    
    if time_format == "iso":
        time_str = now.isoformat()
    elif time_format == "timestamp":
        time_str = str(now.timestamp())
    else:
        time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    
    return CallToolResult(
        content=[{"type": "text", "text": f"当前时间: {time_str}"}]
    )

@server.list_resources()
async def handle_list_resources() -> List[Resource]:
    """列出可用的资源"""
    resources = [
        Resource(
            uri="data://notes",
            name="notes",
            description="所有笔记数据",
            mimeType="application/json"
        ),
        Resource(
            uri="data://config",
            name="config",
            description="配置数据",
            mimeType="application/json"
        )
    ]
    return resources

@server.read_resource()
async def handle_read_resource(uri: str) -> ReadResourceResult:
    """读取资源"""
    try:
        if uri == "data://notes":
            content = json.dumps(data_store["notes"], ensure_ascii=False, indent=2)
            return ReadResourceResult(contents=content)
        elif uri == "data://config":
            content = json.dumps(data_store["config"], ensure_ascii=False, indent=2)
            return ReadResourceResult(contents=content)
        else:
            return ReadResourceResult(contents="资源不存在", isError=True)
    except Exception as e:
        return ReadResourceResult(contents=f"读取资源失败: {str(e)}", isError=True)

@server.write_resource()
async def handle_write_resource(uri: str, contents: str) -> WriteResourceResult:
    """写入资源"""
    try:
        if uri == "data://notes":
            data_store["notes"] = json.loads(contents)
            return WriteResourceResult()
        elif uri == "data://config":
            data_store["config"] = json.loads(contents)
            return WriteResourceResult()
        else:
            return WriteResourceResult(isError=True)
    except Exception as e:
        return WriteResourceResult(isError=True)

async def main():
    """主函数"""
    # 使用stdio服务器
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-demo-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main()) 