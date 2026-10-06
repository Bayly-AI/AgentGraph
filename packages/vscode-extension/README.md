# AgentGraph for Visual Studio Code

[![Visual Studio Marketplace](https://img.shields.io/badge/VS%20Marketplace-AgentGraph-blue.svg)](https://marketplace.visualstudio.com/items?itemName=BaylyAI.agentgraph-vscode)
[![Open VSX](https://img.shields.io/badge/Open%20VSX-AgentGraph-purple.svg)](https://open-vsx.org/extension/BaylyAI/agentgraph-vscode)
[![License](https://img.shields.io/badge/license-GPLv3-green.svg)](LICENSE)
[![Zero External Dependencies](https://img.shields.io/badge/core%20deps-zero%20external-success.svg)](#)

> **Visual Studio Code extension for AgentGraph: Multi-Plane Cognitive Substrate, Topological DAG Dependency Resolver, BM25 Entity Search, and Interactive Mermaid Graph Visualizer for Autonomous AI Agents.**

---

## ⚡ Features

- 🌐 **5-Plane Activity Bar Tree Explorer:**
  - **Agents Plane (`agents`):** Inspect agent roles, tool authorizations, and role hierarchy.
  - **Workflows Plane (`workflows`):** Browse multi-agent execution DAGs, steps, and role mappings.
  - **Rules Plane (`rules`):** View repository directives, branch protection policies, and system invariants.
  - **Knowledge Plane (`knowledge`):** Explore specifications, architecture docs, and cross-references.
  - **Code AST Plane (`code`):** Browse module classes, methods, functions, and import graphs.
- 📊 **Substrate Health & Metric Inspector:** Live node/edge counter, cross-plane edge metrics, and instant DAG topological cycle detection.
- 🎨 **Interactive Mermaid Topology Viewer:** Webview panel with real-time Mermaid.js graph rendering, zoom/pan controls, plane filtering, and dark/light theme integration.
- 🔍 **Sub-Millisecond BM25 Search:** Jump to any rule, workflow step, knowledge entity, or code symbol from the Command Palette.
- ⛓️ **Topological DAG Dependency Resolution:** Resolve upstream and downstream step prerequisites in strict topological execution order.
- 🔄 **Real-time Substrate Sync:** Automatic background synchronization upon saving `AGENTS.md`, `.agentgraph/` configs, or source files.
- 🛡️ **Quality Gate Auditing:** Run repository DAG and test compliance gates directly from the IDE.

---

## 🚀 Quick Start

### 1. Install Extension
Search for **AgentGraph** in the VS Code Extensions panel (`Ctrl+Shift+X` / `Cmd+Shift+X`) and click **Install**.

Or install via terminal:
```bash
code --install-extension release/vscode/plugin/agentgraph-vscode-1.0.0.vsix
```

### 2. Open an AgentGraph-Governed Workspace
Open any repository containing `.agentgraph/` and `AGENTS.md`. The extension automatically activates and loads the 5-plane hierarchy into the Activity Bar.

---

## ⌨️ Commands

| Command | Title | Description |
| :--- | :--- | :--- |
| `agentgraph.sync` | Synchronize Graph Substrate | Ingests workspace files and AST into the SQLite graph |
| `agentgraph.query` | Search Graph (BM25) | Fast entity lookup across all 5 planes |
| `agentgraph.validate` | Validate DAG & Detect Cycles | Audits acyclic graph compliance and dangling edges |
| `agentgraph.resolve` | Resolve DAG Dependencies | Calculates prerequisite execution order for a node |
| `agentgraph.exportMermaid` | View Interactive Mermaid Graph | Opens the interactive visual webview canvas |
| `agentgraph.qualityGate` | Run Quality Gates Audit | Runs complete architecture and test verification |
| `agentgraph.refresh` | Refresh Planes | Refreshes all tree views and status bar metrics |

---

## ⚙️ Configuration Settings

| Setting | Default | Description |
| :--- | :--- | :--- |
| `agentgraph.cliPath` | `""` | Custom path to the `agentgraph` CLI executable. |
| `agentgraph.pythonPath` | `"python3"` | Python interpreter used for fallback engine execution. |
| `agentgraph.dbPath` | `".agentgraph/graph.db"` | Path to the SQLite knowledge graph database. |
| `agentgraph.autoSyncOnSave` | `true` | Automatically re-index when governed files change. |

---

## 📄 License

GNU General Public License v3.0 (GPLv3) — see [LICENSE](LICENSE) for details.
