# AgentGraph Node.js Plugin & SDK

> **High-Performance Multi-Plane Graph Substrate & Cognitive Network Engine for Node.js AI Agents**

[![npm version](https://img.shields.io/npm/v/agentgraph-node-plugin.svg)](https://www.npmjs.com/package/agentgraph-node-plugin)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Zero External Dependencies](https://img.shields.io/badge/dependencies-zero%20external-success.svg)](#)

---

## ⚡ Overview

`agentgraph-node-plugin` connects Node.js applications, TypeScript agents, LangChain JS, Vercel AI SDK, and MCP servers directly into the **AgentGraph Multi-Plane Substrate**.

Features:
- 🚀 **Sub-millisecond BM25 Lexical Node Search** across rules, agents, workflows, knowledge, and code AST.
- 🔗 **Multi-Hop Graph Traversal** (BFS, DFS, shortest paths, neighborhood expansion).
- 🔄 **Topological Dependency Resolution** for agent execution DAGs and code modules.
- 📊 **Automated Topology Health Audit** (Cycle detection, dangling edge elimination).
- 📈 **Mermaid & Graphviz DOT Exporters** for dynamic visual architecture diagramming.

---

## 📦 Installation

```bash
npm install agentgraph-node-plugin
```

---

## 🚀 Quickstart

### 1. Basic Client Usage

```typescript
import { AgentGraphClient } from "agentgraph-node-plugin";

const client = new AgentGraphClient({
  workspaceDir: process.cwd()
});

// 1. Sync workspace into SQLite graph database
await client.sync();

// 2. Perform BM25 lexical search
const results = await client.query("code review", "workflows");
console.log("Found workflow:", results[0]?.node.label);

// 3. Multi-hop traversal
const hops = await client.traverse({
  nodeId: "role:developer",
  direction: "outgoing",
  depth: 2
});
console.log("Connected neighbors:", hops);

// 4. Resolve topological dependencies
const deps = await client.resolveDependencies("workflow:feature_delivery_pipeline");
console.log("Topological execution order:", deps);

// 5. Generate Mermaid diagram
const mermaidDiagram = await client.export("mermaid");
console.log(mermaidDiagram);
```

### 2. Express.js Integration

```typescript
import express from "express";
import { AgentGraphPlugin } from "agentgraph-node-plugin";

const app = express();
const graphPlugin = new AgentGraphPlugin();

app.use(graphPlugin.expressMiddleware());

app.get("/api/graph/stats", async (req, res) => {
  const stats = await req.agentGraph.getStats();
  res.json(stats);
});
```

---

## 📖 API Documentation

For the full TypeScript reference, see [API_REFERENCE.md](API_REFERENCE.md).
