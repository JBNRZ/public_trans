#!/usr/bin/env python3
"""
高级MCP服务器应用
包含更多功能和更好的架构设计
"""

import asyncio
import json
import logging
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from pathlib import Path

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult, ListToolsResult, Tool, Resource,
    ReadResourceResult, WriteResourceResult, ListResourcesResult
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str = "mcp_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建笔记表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建任务表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                priority TEXT DEFAULT 'medium',
                status TEXT DEFAULT 'pending',
                due_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建配置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_note(self, title: str, content: str, tags: List[str] = None) -> int:
        """添加笔记"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        tags_str = json.dumps(tags or [])
        cursor.execute(
            'INSERT INTO notes (title, content, tags) VALUES (?, ?, ?)',
            (title, content, tags_str)
        )
        note_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return note_id
    
    def get_notes(self, limit: int = 10) -> List[Dict]:
        """获取笔记列表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT id, title, content, tags, created_at FROM notes ORDER BY created_at DESC LIMIT ?',
            (limit,)
        )
        
        notes = []
        for row in cursor.fetchall():
            note = {
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'tags': json.loads(row[3]) if row[3] else [],
                'created_at': row[4]
            }
            notes.append(note)
        
        conn.close()
        return notes
    
    def add_task(self, title: str, description: str = "", priority: str = "medium", 
                 due_date: str = None) -> int:
        """添加任务"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO tasks (title, description, priority, due_date) VALUES (?, ?, ?, ?)',
            (title, description, priority, due_date)
        )
        task_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return task_id
    
    def get_tasks(self, status: str = None, priority: str = None) -> List[Dict]:
        """获取任务列表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = 'SELECT id, title, description, priority, status, due_date, created_at FROM tasks'
        params = []
        
        if status or priority:
            conditions = []
            if status:
                conditions.append('status = ?')
                params.append(status)
            if priority:
                conditions.append('priority = ?')
                params.append(priority)
            query += ' WHERE ' + ' AND '.join(conditions)
        
        query += ' ORDER BY created_at DESC'
        
        cursor.execute(query, params)
        
        tasks = []
        for row in cursor.fetchall():
            task = {
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'priority': row[3],
                'status': row[4],
                'due_date': row[5],
                'created_at': row[6]
            }
            tasks.append(task)
        
        conn.close()
        return tasks
    
    def update_task_status(self, task_id: int, status: str) -> bool:
        """更新任务状态"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'UPDATE tasks SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (status, task_id)
        )
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

# 创建MCP服务器实例
server = Server("advanced-mcp-server")

# 创建数据库管理器
db_manager = DatabaseManager()

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
            name="add_task",
            description="添加一个新的任务",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "任务标题"},
                    "description": {"type": "string", "description": "任务描述"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high"], "description": "任务优先级"},
                    "due_date": {"type": "string", "description": "截止日期 (YYYY-MM-DD)"}
                },
                "required": ["title"]
            }
        ),
        Tool(
            name="list_tasks",
            description="列出所有任务",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["pending", "completed"], "description": "任务状态过滤"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high"], "description": "优先级过滤"}
                }
            }
        ),
        Tool(
            name="complete_task",
            description="完成任务",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "任务ID"}
                },
                "required": ["task_id"]
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
        ),
        Tool(
            name="calculate",
            description="执行简单的数学计算",
            inputSchema={
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "数学表达式，如 '2 + 3 * 4'"}
                },
                "required": ["expression"]
            }
        ),
        Tool(
            name="get_weather_info",
            description="获取天气信息（模拟）",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称"}
                },
                "required": ["city"]
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
        elif name == "add_task":
            return await add_task(arguments)
        elif name == "list_tasks":
            return await list_tasks(arguments)
        elif name == "complete_task":
            return await complete_task(arguments)
        elif name == "get_time":
            return await get_time(arguments)
        elif name == "calculate":
            return await calculate(arguments)
        elif name == "get_weather_info":
            return await get_weather_info(arguments)
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
    
    note_id = db_manager.add_note(title, content, tags)
    
    return CallToolResult(
        content=[{
            "type": "text",
            "text": f"笔记已添加: {title}\nID: {note_id}\n内容: {content[:100]}{'...' if len(content) > 100 else ''}"
        }]
    )

async def list_notes(arguments: Dict[str, Any]) -> CallToolResult:
    """列出笔记"""
    limit = arguments.get("limit", 10)
    notes = db_manager.get_notes(limit)
    
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

async def add_task(arguments: Dict[str, Any]) -> CallToolResult:
    """添加任务"""
    title = arguments.get("title", "")
    description = arguments.get("description", "")
    priority = arguments.get("priority", "medium")
    due_date = arguments.get("due_date", "")
    
    task_id = db_manager.add_task(title, description, priority, due_date)
    
    return CallToolResult(
        content=[{
            "type": "text",
            "text": f"任务已添加: {title}\nID: {task_id}\n优先级: {priority}\n状态: 待完成"
        }]
    )

async def list_tasks(arguments: Dict[str, Any]) -> CallToolResult:
    """列出任务"""
    status_filter = arguments.get("status")
    priority_filter = arguments.get("priority")
    
    tasks = db_manager.get_tasks(status_filter, priority_filter)
    
    if not tasks:
        return CallToolResult(
            content=[{"type": "text", "text": "暂无任务"}]
        )
    
    result = "任务列表:\n\n"
    for task in tasks:
        result += f"ID: {task['id']}\n"
        result += f"标题: {task['title']}\n"
        result += f"描述: {task['description']}\n"
        result += f"优先级: {task['priority']}\n"
        result += f"状态: {task['status']}\n"
        result += f"截止日期: {task['due_date'] if task['due_date'] else '无'}\n"
        result += f"创建时间: {task['created_at']}\n"
        result += "-" * 50 + "\n"
    
    return CallToolResult(
        content=[{"type": "text", "text": result}]
    )

async def complete_task(arguments: Dict[str, Any]) -> CallToolResult:
    """完成任务"""
    task_id = arguments.get("task_id")
    
    if db_manager.update_task_status(task_id, "completed"):
        return CallToolResult(
            content=[{"type": "text", "text": f"任务 {task_id} 已完成"}]
        )
    else:
        return CallToolResult(
            content=[{"type": "text", "text": f"任务 {task_id} 不存在或更新失败"}],
            isError=True
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

async def calculate(arguments: Dict[str, Any]) -> CallToolResult:
    """执行数学计算"""
    expression = arguments.get("expression", "")
    
    try:
        # 安全地执行数学表达式
        allowed_names = {
            'abs': abs, 'round': round, 'min': min, 'max': max,
            'sum': sum, 'len': len, 'int': int, 'float': float
        }
        
        # 构建安全的表达式
        safe_expression = expression.replace('__', '').replace('import', '').replace('eval', '')
        
        result = eval(safe_expression, {"__builtins__": {}}, allowed_names)
        
        return CallToolResult(
            content=[{"type": "text", "text": f"计算结果: {expression} = {result}"}]
        )
    except Exception as e:
        return CallToolResult(
            content=[{"type": "text", "text": f"计算错误: {str(e)}"}],
            isError=True
        )

async def get_weather_info(arguments: Dict[str, Any]) -> CallToolResult:
    """获取天气信息（模拟）"""
    city = arguments.get("city", "北京")
    
    # 模拟天气数据
    weather_data = {
        "北京": {"temperature": "22°C", "condition": "晴天", "humidity": "45%"},
        "上海": {"temperature": "25°C", "condition": "多云", "humidity": "60%"},
        "广州": {"temperature": "28°C", "condition": "小雨", "humidity": "75%"},
        "深圳": {"temperature": "26°C", "condition": "阴天", "humidity": "70%"}
    }
    
    weather = weather_data.get(city, {"temperature": "20°C", "condition": "未知", "humidity": "50%"})
    
    result = f"{city}天气信息:\n"
    result += f"温度: {weather['temperature']}\n"
    result += f"天气状况: {weather['condition']}\n"
    result += f"湿度: {weather['humidity']}"
    
    return CallToolResult(
        content=[{"type": "text", "text": result}]
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
            uri="data://tasks", 
            name="tasks",
            description="所有任务数据",
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
            notes = db_manager.get_notes(1000)  # 获取所有笔记
            content = json.dumps(notes, ensure_ascii=False, indent=2)
            return ReadResourceResult(contents=content)
        elif uri == "data://tasks":
            tasks = db_manager.get_tasks()  # 获取所有任务
            content = json.dumps(tasks, ensure_ascii=False, indent=2)
            return ReadResourceResult(contents=content)
        elif uri == "data://config":
            content = json.dumps({"version": "1.0.0", "server": "advanced-mcp-server"}, ensure_ascii=False, indent=2)
            return ReadResourceResult(contents=content)
        else:
            return ReadResourceResult(contents="资源不存在", isError=True)
    except Exception as e:
        return ReadResourceResult(contents=f"读取资源失败: {str(e)}", isError=True)

async def main():
    """主函数"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="advanced-mcp-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main()) 