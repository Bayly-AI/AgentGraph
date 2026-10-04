# AgentGraph Model Context Protocol (MCP) & Claude Integration Guide

> **Integration Standard:** Model Context Protocol (MCP) Stdio JSON-RPC 2.0  
> **Supported Clients:** Claude Desktop, Claude Code CLI, Cursor, Windsurf, FastMCP  

---

## 1. Overview

AgentGraph provides a native **Model Context Protocol (MCP)** server (`agentgraph mcp`), enabling Anthropic **Claude Desktop** and **Claude Code CLI** to query the cognitive graph substrate, traverse multi-agent networks, resolve step DAGs, and generate visual Mermaid diagrams directly during conversations.

---

## 2. Claude Desktop Integration (`claude_desktop_config.json`)

To register AgentGraph in **Claude Desktop**:

1. Open your Claude Desktop configuration file:
   - **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
2. Add the `agentgraph` MCP server entry:

```json
{
  "mcpServers": {
    "agentgraph": {
      "command": "agentgraph",
      "args": ["mcp", "--dir", "/path/to/your/workspace"]
    }
  }
}
```

If using the standalone binary release directly:

```json
{
  "mcpServers": {
    "agentgraph": {
      "command": "/usr/local/bin/agentgraph",
      "args": ["mcp", "--dir", "/Users/username/Development/OpenSource/AgentGraph"]
    }
  }
}
```

---

## 3. Claude Code CLI Integration

To attach AgentGraph MCP tools to **Claude Code CLI**:

```bash
claude mcp add agentgraph agentgraph mcp --dir .
```

---

## 4. Exposed MCP Tool Surface

When connected to Claude Desktop or Claude Code, AgentGraph exposes 7 governed graph tools:

| MCP Tool Name | Function Purpose | Input Parameters |
| :--- | :--- | :--- |
| `agentgraph_query` | BM25 lexical search across graph nodes | `query` (string), `plane` (optional enum), `limit` (int) |
| `agentgraph_traverse` | BFS graph exploration and neighbor traversal | `node_id` (string), `direction` (enum), `depth` (int), `relation` (string) |
| `agentgraph_resolve` | Topological upstream/downstream dependency resolution | `node_id` (string) |
| `agentgraph_validate` | Topology health check (cycles, dangling edges) | `dir` (optional string) |
| `agentgraph_export` | Visual diagram generator (Mermaid / DOT / JSON) | `format` (enum), `plane` (optional enum) |
| `agentgraph_sync` | Synchronize workspace files and AST into graph | `dir` (optional string) |
| `agentgraph_stats` | Retrieve topological counts across all planes | *(none)* |

---

## 5. Publishing to MCP Registries (Smithery / Glama / PulseMCP)

AgentGraph is configured for 1-click deployment on public MCP registries:

- **Smithery.ai:** `smithery install agentgraph`
- **Glama.ai:** Listed under Agent Memory & Knowledge Graph
- **PulseMCP:** Multi-Plane Cognitive Substrate Category
