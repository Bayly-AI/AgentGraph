# AgentGraph Runtime Integration Guide

This guide describes how to integrate AgentGraph into Python applications, Node.js runtimes, LangChain, and Vercel AI SDK.

---

## 1. Python SDK Integration

```python
from agentgraph import AgentGraph, AgentGraphPlane

# Initialize or load graph
graph = AgentGraph.init(workspace_dir=".")

# BM25 Search
results = graph.query("developer", plane=AgentGraphPlane.AGENTS.value)
for r in results:
    print(r.node.label, r.score)

# BFS Traversal
hops = graph.traverse(start_node_id="role:developer", direction="outgoing", max_depth=2)

# Topological Dependency Resolution
deps = graph.resolve_dependencies("workflow:feature_delivery_pipeline")
```

---

## 2. Node.js / TypeScript SDK Integration

```typescript
import { AgentGraphClient } from "agentgraph-node-plugin";

const client = new AgentGraphClient();

// Synchronize workspace
await client.sync();

// Search
const results = await client.query("review", "workflows");

// Export Mermaid diagram
const mermaid = await client.export("mermaid");
```

---

## 3. Express.js Middleware Integration

```typescript
import express from "express";
import { AgentGraphPlugin } from "agentgraph-node-plugin";

const app = express();
const graphPlugin = new AgentGraphPlugin();

app.use(graphPlugin.expressMiddleware());

app.get("/api/graph/traverse/:nodeId", async (req, res) => {
  const hops = await req.agentGraph.traverse({
    nodeId: req.params.nodeId,
    depth: 2
  });
  res.json(hops);
});
```
