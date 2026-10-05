"""Model Context Protocol (MCP) Stdio JSON-RPC 2.0 server for Claude Desktop and Claude Code."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

from agentgraph.core.graph import AgentGraphEngine
from agentgraph.export.exporter import GraphExporter
from agentgraph.sync.syncer import RepositorySyncer


class AgentGraphMCPServer:
    """Stdio MCP server exposing AgentGraph tools to Claude Desktop, Claude Code, and Cursor."""

    def __init__(self, workspace_dir: str = ".") -> None:
        self.workspace_dir = Path(workspace_dir).resolve()
        self.db_path = self.workspace_dir / ".agentgraph" / "graph.db"

    def get_tools_list(self) -> List[Dict[str, Any]]:
        """Return MCP tools manifest."""
        return [
            {
                "name": "agentgraph_query",
                "description": "Performs fast BM25 lexical search across all nodes in the AgentGraph cognitive substrate (rules, agents, workflows, knowledge, and code AST).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query keywords or concept phrases"},
                        "plane": {
                            "type": "string",
                            "enum": ["rules", "agents", "workflows", "knowledge", "code"],
                            "description": "Optional graph plane filter"
                        },
                        "limit": {"type": "integer", "default": 10, "description": "Maximum ranked results to return"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "agentgraph_traverse",
                "description": "Explores connected neighbor nodes and relational paths starting from a specific node ID.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "node_id": {"type": "string", "description": "Root starting node ID (e.g., 'role:developer', 'ast:mod:cli')"},
                        "direction": {"type": "string", "enum": ["outgoing", "incoming", "both"], "default": "outgoing"},
                        "max_depth": {"type": "integer", "default": 3, "description": "Maximum hop depth"},
                        "relation": {"type": "string", "description": "Optional edge relation filter (e.g. 'DEPENDS_ON', 'ASSIGNED_TO')"}
                    },
                    "required": ["node_id"]
                }
            },
            {
                "name": "agentgraph_resolve",
                "description": "Resolves all upstream and downstream dependencies for a given node in topological order.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "node_id": {"type": "string", "description": "Node ID to resolve dependencies for"}
                    },
                    "required": ["node_id"]
                }
            },
            {
                "name": "agentgraph_validate",
                "description": "Audits graph topology for circular dependencies, dangling edges, and isolated disconnected nodes.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "dir": {"type": "string", "default": ".", "description": "Workspace root directory"}
                    }
                }
            },
            {
                "name": "agentgraph_export",
                "description": "Exports graph topology as a Mermaid diagram, Graphviz DOT format, or structured JSON.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "format": {"type": "string", "enum": ["mermaid", "dot", "json"], "default": "mermaid"},
                        "plane": {
                            "type": "string",
                            "enum": ["rules", "agents", "workflows", "knowledge", "code"],
                            "description": "Optional plane filter"
                        }
                    }
                }
            },
            {
                "name": "agentgraph_sync",
                "description": "Scans workspace directory files, AST code, rules, workflows, and documentation into the graph database.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "dir": {"type": "string", "default": ".", "description": "Target workspace directory"}
                    }
                }
            },
            {
                "name": "agentgraph_stats",
                "description": "Retrieves statistical summary metrics across all graph planes, node types, and edge relations.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]

    def handle_tool_call(self, name: str, args: Dict[str, Any]) -> str:
        """Route tool invocation and return string response."""
        graph = AgentGraphEngine(db_path=self.db_path)
        if self.db_path.exists():
            try:
                graph.load_from_db()
            except (OSError, ValueError, json.JSONDecodeError):
                pass

        if name == "agentgraph_query":
            q = args.get("query", "")
            plane = args.get("plane")
            limit = int(args.get("limit", 10))
            results = graph.query(query_str=q, plane=plane, limit=limit)
            return json.dumps([r.to_dict() for r in results], indent=2)

        elif name == "agentgraph_traverse":
            node_id = args.get("node_id", "")
            direction = args.get("direction", "outgoing")
            max_depth = int(args.get("max_depth", 3))
            relation = args.get("relation")
            hops = graph.traverse(
                start_node_id=node_id,
                direction=direction,
                max_depth=max_depth,
                relation_filter=relation
            )
            return json.dumps(hops, indent=2)

        elif name == "agentgraph_resolve":
            node_id = args.get("node_id", "")
            deps = graph.resolve_dependencies(node_id)
            return json.dumps({"node_id": node_id, "topological_dependencies": deps}, indent=2)

        elif name == "agentgraph_validate":
            rep = graph.validate()
            return json.dumps(rep.to_dict(), indent=2)

        elif name == "agentgraph_export":
            fmt = args.get("format", "mermaid")
            plane = args.get("plane")
            if fmt == "mermaid":
                return GraphExporter.to_mermaid(graph, plane=plane)
            elif fmt == "dot":
                return GraphExporter.to_dot(graph, plane=plane)
            else:
                return GraphExporter.to_json(graph)

        elif name == "agentgraph_sync":
            target_dir = args.get("dir", str(self.workspace_dir))
            synced_graph = RepositorySyncer.sync_repository(root_dir=target_dir, db_path=self.db_path)
            stats = synced_graph.get_stats()
            return json.dumps({"status": "SUCCESS", "stats": stats}, indent=2)

        elif name == "agentgraph_stats":
            return json.dumps(graph.get_stats(), indent=2)

        return f"Unknown tool name: {name}"

    def run_stdio(self) -> None:
        """Run standard I/O JSON-RPC 2.0 loop."""
        while True:
            line = sys.stdin.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue

            try:
                req = json.loads(line)
            except (json.JSONDecodeError, ValueError, TypeError):
                continue

            req_id = req.get("id")
            method = req.get("method")

            if method == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "agentgraph", "version": "1.0.0"},
                    },
                }
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()

            elif method == "notifications/initialized":
                pass

            elif method == "ping":
                resp = {"jsonrpc": "2.0", "id": req_id, "result": {}}
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()

            elif method == "tools/list":
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"tools": self.get_tools_list()},
                }
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()

            elif method == "tools/call":
                params = req.get("params", {})
                tool_name = params.get("name", "")
                tool_args = params.get("arguments", {})
                res_text = self.handle_tool_call(tool_name, tool_args)
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": res_text}],
                        "isError": False,
                    },
                }
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()

            else:
                if req_id is not None:
                    resp = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "error": {"code": -32601, "message": f"Method not found: {method}"},
                    }
                    sys.stdout.write(json.dumps(resp) + "\n")
                    sys.stdout.flush()


def run_mcp_server(workspace_dir: str = ".") -> None:
    server = AgentGraphMCPServer(workspace_dir=workspace_dir)
    server.run_stdio()
