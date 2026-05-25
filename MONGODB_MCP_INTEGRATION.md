# MongoDB MCP Server Integration

This document explains how the PuckMind Hockey Agent integrates the MongoDB MCP (Model Context Protocol) server as required by the Google Cloud Rapid Agent Hackathon.

## What is MCP?

Model Context Protocol (MCP) is an open-source standard for connecting AI applications to external systems. It provides a standardized way for AI agents to access data sources like databases through a secure, structured protocol.

## MongoDB MCP Server

We use the official MongoDB MCP server (`mongodb-js/mongodb-mcp-server`) which provides:
- 16+ MongoDB database tools (aggregate, find, count, etc.)
- Secure connection to MongoDB Atlas
- Read-only mode for safe data access
- Structured query execution through the protocol

## Integration Architecture

```
Google ADK Agent (Python)
         ↓
   Python MCP SDK
         ↓
MongoDB MCP Server (Node.js)
         ↓
   MongoDB Atlas
```

## Implementation

### 1. MCP Server Setup

The MongoDB MCP server runs as a subprocess and communicates via stdin/stdout:

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="npx",
    args=["-y", "mongodb-mcp-server@latest", "--readOnly"],
    env={"MDB_MCP_CONNECTION_STRING": MONGODB_URI}
)
```

### 2. Available MCP Tools

The MongoDB MCP server exposes these tools to our agent:

- `aggregate` - Run aggregation pipelines
- `count` - Count documents
- `collection-schema` - Describe collection structure
- `db-stats` - Database statistics
- `find` - Query documents
- `collection-indexes` - List indexes
- And 10+ more database operations

### 3. Agent Integration

Our agent uses MCP tools for database operations:

```python
# Example: Get database statistics via MCP
async def get_db_stats_mcp():
    result = await mcp_session.call_tool(
        "db-stats",
        arguments={"database": "hockey_agent"}
    )
    return result
```

## Benefits of MCP Integration

1. **Standardized Access**: Uses the official MongoDB MCP protocol
2. **Security**: Read-only mode prevents accidental data modification  
3. **Monitoring**: All database operations are logged through the protocol
4. **Portability**: Can switch between MCP-compatible clients (Claude Desktop, VS Code, etc.)
5. **Future-proof**: Built on an open standard supported by major AI platforms

## Testing the Integration

To verify MCP integration is working:

```bash
cd /Users/christianmeyndt/PyCharmMiscProject/puckmind
source venv/bin/activate
python src/agent_mcp.py
```

This will:
1. Start the MongoDB MCP server
2. Connect to MongoDB Atlas via MCP
3. List available MCP tools (16 tools)
4. Run a test query through MCP
5. Display the results

## Hackathon Compliance

✅ Uses official MongoDB MCP server (`mongodb-js/mongodb-mcp-server`)  
✅ Integrates via Model Context Protocol (Python MCP SDK)  
✅ Connects to MongoDB Atlas through MCP  
✅ Demonstrates MCP tool usage  
✅ Read-only mode for safe operation  

## Files

- `src/agent_mcp.py` - MCP integration test script
- `src/agent_with_mcp.py` - Full agent with MCP integration
- `.env` - MongoDB connection string (MDB_MCP_CONNECTION_STRING)

## Dependencies

```
mcp==1.27.1              # Python MCP SDK
mongodb-mcp-server       # Node.js MCP server (via npx)
```

## References

- MongoDB MCP Server: https://github.com/mongodb-js/mongodb-mcp-server
- Model Context Protocol: https://modelcontextprotocol.io
- MCP Python SDK: https://pypi.org/project/mcp/
