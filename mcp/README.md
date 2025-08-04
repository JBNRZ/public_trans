# MCP 服务器应用

这是一个基于 Model Context Protocol (MCP) 的完整服务器应用，提供了多种工具和资源管理功能。

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 运行演示
```bash
python demo.py
```

### 3. 启动服务器
```bash
python simple_mcp_server.py
```

## 📁 项目结构

```
mcp/
├── simple_mcp_server.py    # 简单MCP服务器
├── advanced_mcp_server.py  # 高级MCP服务器（带数据库）
├── demo.py                # 演示脚本
├── test_mcp.py            # 测试脚本
├── run_server.py          # 启动脚本
├── config.json            # 配置文件
├── requirements.txt       # Python依赖
└── README.md             # 项目说明
```

## 🛠️ 功能特性

### 工具 (Tools)

#### 基础工具
- **add_note**: 添加新的笔记
- **list_notes**: 列出所有笔记
- **get_time**: 获取当前时间

#### 高级工具 (advanced_mcp_server.py)
- **add_task**: 添加新任务
- **list_tasks**: 列出所有任务
- **complete_task**: 完成任务
- **calculate**: 数学计算
- **get_weather_info**: 获取天气信息（模拟）

### 资源 (Resources)
- **data://notes**: 笔记数据资源
- **data://tasks**: 任务数据资源
- **data://config**: 配置数据资源

## 📖 使用示例

### 添加笔记
```json
{
  "name": "add_note",
  "arguments": {
    "title": "我的第一个笔记",
    "content": "这是一个测试笔记的内容"
  }
}
```

### 列出笔记
```json
{
  "name": "list_notes",
  "arguments": {
    "limit": 10
  }
}
```

### 获取时间
```json
{
  "name": "get_time",
  "arguments": {
    "format": "iso"
  }
}
```

### 添加任务
```json
{
  "name": "add_task",
  "arguments": {
    "title": "完成项目",
    "description": "完成MCP应用开发",
    "priority": "high",
    "due_date": "2024-01-15"
  }
}
```

## 🔧 开发说明

### MCP协议实现
这个MCP服务器实现了以下MCP协议功能：

1. **工具列表**: 通过 `@server.list_tools()` 装饰器提供可用工具列表
2. **工具调用**: 通过 `@server.call_tool()` 装饰器处理工具调用
3. **资源管理**: 支持资源的读取和写入操作
4. **错误处理**: 包含完整的错误处理机制

### 服务器类型

#### 简单服务器 (simple_mcp_server.py)
- 使用内存存储
- 基础功能实现
- 适合学习和测试

#### 高级服务器 (advanced_mcp_server.py)
- 使用SQLite数据库
- 完整的功能实现
- 支持数据持久化
- 更多工具和功能

## 🧪 测试

运行测试脚本：
```bash
python test_mcp.py
```

## 📊 配置

编辑 `config.json` 文件来自定义服务器配置：

```json
{
  "server": {
    "name": "mcp-demo-server",
    "version": "1.0.0"
  },
  "database": {
    "type": "sqlite",
    "path": "mcp_data.db"
  }
}
```

## 🔄 扩展功能

你可以通过以下方式扩展这个MCP服务器：

1. **添加新工具**: 在服务器文件中添加新的工具函数
2. **数据库支持**: 集成其他数据库（MySQL, PostgreSQL等）
3. **API集成**: 添加外部API调用功能
4. **安全验证**: 实现认证和授权机制
5. **日志记录**: 添加详细的日志记录功能

## ⚠️ 注意事项

- 简单服务器使用内存存储，重启后数据会丢失
- 高级服务器使用SQLite数据库，数据会持久化保存
- 建议在生产环境中使用更安全的配置
- 可以根据需要添加更多的错误处理和验证

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📄 许可证

本项目采用MIT许可证。 