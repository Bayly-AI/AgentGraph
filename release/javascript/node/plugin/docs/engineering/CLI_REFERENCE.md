# AgentGraph CLI Reference

The `agentgraph` CLI provides command-line tools for graph initialization, workspace synchronization, BM25 searching, traversal, dependency resolution, validation, export, and MCP serving.

---

## Commands

### `agentgraph init`
Initializes `.agentgraph/` directory structure, default templates, `AGENTS.md`, and git pre-commit hooks.

```bash
agentgraph init [--dir <path>] [--no-hooks]
```

### `agentgraph sync`
Crawls workspace files (`AGENTS.md`, `.agentgraph/rules/*.json`, `.agentgraph/agents/*.json`, `.agentgraph/workflows/*.json`, `docs/`, `agentgraph/`, `src/`) and updates the SQLite graph database.

```bash
agentgraph sync [--dir <path>] [--db <path>]
```

### `agentgraph query`
Executes BM25 lexical ranking across all nodes or a specific plane.

```bash
agentgraph query <query_string> [--plane <rules|agents|workflows|knowledge|code>] [--limit <n>] [--db <path>] [--json]
```

### `agentgraph traverse`
Performs Breadth-First Search traversal starting from a node.

```bash
agentgraph traverse <node_id> [--depth <n>] [--direction <outgoing|incoming|both>] [--relation <rel>] [--db <path>] [--json]
```

### `agentgraph resolve`
Resolves upstream and downstream dependencies for a node in topological order.

```bash
agentgraph resolve <node_id> [--db <path>] [--json]
```

### `agentgraph validate`
Audits graph topology for circular dependencies, dangling edges, and isolated disconnected nodes.

```bash
agentgraph validate [--dir <path>] [--db <path>] [--json]
```

### `agentgraph export`
Exports graph topology to Mermaid diagram, Graphviz DOT format, or JSON.

```bash
agentgraph export [--format <mermaid|dot|json>] [--plane <plane>] [--db <path>] [--out <file>]
```

### `agentgraph stats`
Displays summary counts of nodes, edges, planes, and relation types.

```bash
agentgraph stats [--db <path>] [--json]
```

### `agentgraph quality-gate`
Executes the automated 4-Gate Quality Verification suite.

```bash
agentgraph quality-gate [--dir <path>] [--db <path>] [--json]
```

### `agentgraph mcp`
Runs the Model Context Protocol stdio JSON-RPC 2.0 server.

```bash
agentgraph mcp [--dir <path>]
```
