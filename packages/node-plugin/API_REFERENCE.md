# AgentGraph Node.js Plugin API Reference

## Classes

### `AgentGraphClient`

Core client for executing graph queries, traversals, and management operations.

#### Constructor
```typescript
new AgentGraphClient(options?: PluginOptions)
```
- `options.workspaceDir` *(string, optional)*: Workspace root directory. Defaults to `process.cwd()`.
- `options.cliPath` *(string, optional)*: Explicit path to `agentgraph` CLI binary.
- `options.dbPath` *(string, optional)*: Path to SQLite graph database. Defaults to `.agentgraph/graph.db`.

#### Methods

- **`init(noHooks?: boolean): Promise<string>`**  
  Scaffolds workspace hierarchy (`.agentgraph/`, `AGENTS.md`, and git hooks).

- **`sync(): Promise<string>`**  
  Scans workspace files, rules, workflows, and code AST into the database.

- **`query(queryText: string, plane?: AgentGraphPlane, limit?: number): Promise<SearchResult[]>`**  
  Executes BM25 lexical search ranking across nodes.

- **`traverse(options: { nodeId: string; direction?: "outgoing" | "incoming" | "both"; depth?: number; relation?: string }): Promise<TraversalHop[]>`**  
  Executes BFS traversal from a root node.

- **`resolveDependencies(nodeId: string): Promise<string[]>`**  
  Resolves upstream/downstream dependencies in topological order.

- **`validate(): Promise<GraphValidationReport>`**  
  Validates graph health and reports cycles, dangling edges, and isolated nodes.

- **`export(format?: "mermaid" | "dot" | "json", plane?: AgentGraphPlane): Promise<string>`**  
  Exports graph structure in visual diagram or JSON syntax.

- **`getStats(): Promise<GraphStats>`**  
  Retrieves metric counts for nodes, edges, planes, and relations.

- **`runQualityGate(): Promise<{ success: boolean; output: string }>`**  
  Executes the automated 4-Gate Quality validation suite.

---

### `AgentGraphPlugin`

High-level wrapper and framework integration helper.

#### Methods
- **`expressMiddleware()`**: Connect / Express middleware attaching `req.agentGraph`.
