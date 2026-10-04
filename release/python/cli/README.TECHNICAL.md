# AgentGraph: Technical Architecture & Engineering Reference

> **Document Version:** 1.0.0  
> **Repository:** Bayly-AI/AgentGraph  
> **Maintainer:** Ray Bayly (ray@bayly.ai)  

---

## 1. System Overview & Architecture

AgentGraph is an open-source, multi-plane cognitive graph substrate and runtime engine. It addresses the need for structured, deterministic knowledge representation and DAG execution topology in multi-agent autonomous AI environments.

```
+-----------------------------------------------------------------------------------+
|                               AGENTGRAPH PLATFORM                                 |
+-----------------------------------------------------------------------------------+
|  [CLI Interface]            [Node.js SDK]              [Claude MCP Server]        |
|  agentgraph init/sync/query  agentgraph-node-plugin     JSON-RPC 2.0 Stdio Tools    |
+-----------------------------------------------------------------------------------+
                                      │
                                      ▼
+-----------------------------------------------------------------------------------+
|                              AGENTGRAPH ENGINE                                    |
|                                                                                   |
|  ┌─────────────────────┐  ┌───────────────────────┐  ┌─────────────────────────┐  |
|  │  BM25 Search Index  │  │ Graph Traversal (BFS) │  │ DAG Topological Resolver│  |
|  └─────────────────────┘  └───────────────────────┘  └─────────────────────────┘  |
+-----------------------------------------------------------------------------------+
                                      │
                                      ▼
+-----------------------------------------------------------------------------------+
|                        5-PLANE HETEROGENEOUS TOPOLOGY                             |
|                                                                                   |
|  [Agents]        Roles, capabilities, tools, parent inheritance hierarchies       |
|  [Workflows]     DAG step sequences, pipeline dependencies, agent assignments     |
|  [Knowledge]     Markdown docs, system specifications, cross-references           |
|  [Code AST]      Python/TS modules, classes, functions, inheritance links         |
|  [Rules]         Directives, invariants, scoping standards                        |
+-----------------------------------------------------------------------------------+
                                      │
                                      ▼
+-----------------------------------------------------------------------------------+
|                     ATOMIC PERSISTENCE LAYER (SQLite3)                            |
|                     .agentgraph/graph.db (nodes, edges, indexes)                  |
+-----------------------------------------------------------------------------------+
```

---

## 2. Core Python Architecture

### 2.1 Storage Layer (`agentgraph.core.storage.SQLiteStore`)
- Stores nodes and edges in SQLite with atomic transactions and explicit index acceleration (`idx_nodes_plane`, `idx_edges_source`, `idx_edges_target`, `idx_edges_relation`).
- Zero external ORM overhead: pure Python standard library `sqlite3`.

### 2.2 Lexical Search Engine (`agentgraph.core.search.BM25SearchEngine`)
- Okapi BM25 ranking algorithm ($k_1=1.5, b=0.75$) with smoothed Inverse Document Frequency (IDF).
- Indexes node labels, types, planes, content text, and properties dictionary.

### 2.3 Traversal & Topological Resolver (`agentgraph.core.traversal.GraphTraversalEngine`)
- **BFS Traversal:** Multi-hop neighborhood expansion with depth bounding and relation filters.
- **Pathfinding:** Acyclic path exploration between source and target nodes.
- **Topological Sorting:** Kahn's algorithm for dependency ordering.
- **Cycle Detection:** DFS with recursion-stack backtracking.

### 2.4 Code & Markdown Parsers (`agentgraph.sync`)
- `CodeASTParser`: Inspects Python AST syntax trees (`ast.parse`) and TypeScript/JavaScript class/function definitions to build Code plane nodes and `INHERITS_FROM`, `CONTAINS_CLASS`, `CONTAINS_FUNCTION` edges.
- `MarkdownParser`: Extracts directives, headers, and relative link cross-references from `AGENTS.md` and documentation hierarchies.

---

## 3. Node.js Plugin Architecture (`packages/node-plugin`)

The Node.js package `agentgraph-node-plugin` wraps the high-performance CLI/engine and provides a fully typed TypeScript client:

```typescript
import { AgentGraphClient } from "agentgraph-node-plugin";

const client = new AgentGraphClient();

// Synchronous and asynchronous command execution
const results = await client.query("search query", "code");
const mermaid = await client.export("mermaid");
const stats = await client.getStats();
```

---

## 4. MCP Server & Claude Integration (`agentgraph.mcp`)

AgentGraph implements the standard Model Context Protocol (MCP) JSON-RPC 2.0 stdio specification.

Exposed MCP Tools:
1. `agentgraph_query`: BM25 lexical search across planes.
2. `agentgraph_traverse`: Breadth-first graph exploration.
3. `agentgraph_resolve`: Topological dependency resolution.
4. `agentgraph_validate`: Graph health audit (cycles/dangling edges).
5. `agentgraph_export`: Mermaid, Graphviz DOT, or JSON serialization.
6. `agentgraph_sync`: Ingest workspace code and documentation.
7. `agentgraph_stats`: Topological summary statistics.

---

## 5. Quality Gates & Release Packaging

AgentGraph enforces a 4-Gate Quality Verification standard:
1. **Gate 1: Workspace Synchronization:** Full filesystem crawl and graph indexing.
2. **Gate 2: Topology Health:** Strict acyclic DAG verification (0 cycles, 0 dangling edges).
3. **Gate 3: Unit Test Suite:** 100% test passing rate across all modules.
4. **Gate 4: Build Package Verification:** Standalone zipapp executable (`release/python/cli/agentgraph`) and npm tarball.
