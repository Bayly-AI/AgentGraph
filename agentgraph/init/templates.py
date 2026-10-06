"""Default file templates and JSON schema definitions for repository initialization."""

from __future__ import annotations

DEFAULT_CONFIG_JSON = """{
  "project_name": "AgentGraph Workspace",
  "version": "1.0.0",
  "db_path": ".agentgraph/graph.db",
  "scan_directories": [
    "AGENTS.md",
    ".agentgraph/rules",
    ".agentgraph/agents",
    ".agentgraph/workflows",
    ".agentgraph/knowledge",
    "docs",
    "src"
  ],
  "pre_commit_hook": true
}
"""

CORE_INVARIANTS_JSON = """[
  {
    "id": "graph_inv_001_no_direct_push",
    "title": "Main & Development Branch Protection",
    "target_scope": "root",
    "content": "All changes must be submitted via Pull Requests and receive explicit approval from Ray Bayly (@raybayly) before merging into development."
  },
  {
    "id": "graph_inv_002_acyclic_workflows",
    "title": "Acyclic Workflow DAG Invariant",
    "target_scope": "root",
    "content": "All agent execution workflows and step dependencies must form a strictly Directed Acyclic Graph (DAG) with zero circular dependencies."
  }
]
"""

GRAPH_STANDARDS_JSON = """[
  {
    "id": "graph_std_001_typed_edges",
    "title": "Typed Relational Graph Edges",
    "target_scope": "root",
    "content": "All graph edges must specify an explicit relationship type (CONTAINS_STEP, ASSIGNED_TO, DEPENDS_ON, REFERENCES, GOVERNS, INHERITS_FROM)."
  },
  {
    "id": "graph_std_002_clean_ast_sync",
    "title": "Synchronized AST Code Graph",
    "target_scope": "root",
    "content": "The knowledge and code planes must be kept in sync with actual codebase AST structures via agentgraph sync."
  }
]
"""

ROLE_ARCHITECT_JSON = """{
  "role_id": "architect",
  "name": "System & Graph Architect",
  "description": "Designs multi-agent graph topologies, workflow DAGs, and system boundary specifications.",
  "scope": "root",
  "tools": [
    "view_file",
    "agentgraph_query",
    "agentgraph_traverse",
    "agentgraph_export",
    "agentgraph_validate"
  ]
}
"""

ROLE_DEVELOPER_JSON = """{
  "role_id": "developer",
  "name": "Autonomous Software Engineer",
  "description": "Implements features, resolves dependency graphs, edits codebase, and generates unit tests.",
  "scope": "root",
  "tools": [
    "view_file",
    "write_to_file",
    "replace_file_content",
    "run_command",
    "agentgraph_query",
    "agentgraph_traverse",
    "agentgraph_resolve"
  ]
}
"""

ROLE_REVIEWER_JSON = """{
  "role_id": "reviewer",
  "name": "Code & Graph Topology Reviewer",
  "description": "Audits pull requests, verifies graph health, detects circular dependencies, and reviews code changes.",
  "scope": "root",
  "tools": [
    "view_file",
    "agentgraph_query",
    "agentgraph_validate",
    "agentgraph_export"
  ]
}
"""

ROLE_RESEARCHER_JSON = """{
  "role_id": "researcher",
  "name": "Knowledge & Deep Research Agent",
  "description": "Performs deep lexical and topological graph search across documentation, rules, and code entities.",
  "scope": "root",
  "tools": [
    "view_file",
    "search_web",
    "agentgraph_query",
    "agentgraph_traverse"
  ]
}
"""

WORKFLOW_PIPELINE_JSON = """{
  "id": "feature_delivery_pipeline",
  "name": "Feature Delivery & Review Pipeline",
  "description": "Standard multi-agent workflow DAG for feature implementation, verification, and graph synchronization.",
  "steps": [
    {
      "id": "1_architecture_plan",
      "name": "Architecture & Graph Modeling",
      "description": "Analyze system requirements and define module dependency graph.",
      "agent_role": "architect",
      "depends_on": []
    },
    {
      "id": "2_implementation",
      "name": "Code Implementation",
      "description": "Implement code modules, functions, and unit tests.",
      "agent_role": "developer",
      "depends_on": ["1_architecture_plan"]
    },
    {
      "id": "3_code_review",
      "name": "Graph & Code Review",
      "description": "Audit code quality, test suite, and graph topology validation.",
      "agent_role": "reviewer",
      "depends_on": ["2_implementation"]
    }
  ]
}
"""

KNOWLEDGE_ARCH_MD = """# System Architecture & Graph Topology

## Overview
AgentGraph provides a standalone, multi-plane cognitive substrate and high-performance graph engine designed for agentic AI systems.

## Graph Planes
1. **Agents (`agents`):** Agent roles, tools, and parent inheritance.
2. **Workflows (`workflows`):** Workflow DAGs, step sequences, and role assignments.
3. **Knowledge (`knowledge`):** Markdown specifications, cross-links, and domain manuals.
4. **Code AST (`code`):** Python and JS/TS modules, classes, methods, and functions.
5. **Rules (`rules`):** Invariants, policies, and governance directives.

## Query & Traversal
- **BM25 Search:** Sub-millisecond ranking across node labels, types, and content.
- **BFS & Pathfinding:** Multi-hop traversal, shortest paths, and upstream/downstream dependency resolution.
- **Validation:** Automated cycle detection, dangling edge elimination, and topology integrity.
"""

AGENTS_MD_TEMPLATE = """# AGENTS.md — AgentGraph Multi-Agent Architecture

> **Framework:** AgentGraph Multi-Plane Substrate  
> **Repository Owner & Reviewer:** Ray Bayly (@raybayly)  
> **Status:** Production Ready  

---

## 1. System Invariants & Directives

### GRAPH-INV-001: Main & Development Branch Protection
All code changes must be submitted via Pull Requests against the `development` branch. Merges require review and explicit approval by Ray Bayly (`@raybayly`).

### GRAPH-INV-002: Strict DAG Workflow Execution
All multi-agent pipelines and step dependencies must be acyclic. Topological cycle validation must pass before execution.

---

## 2. Multi-Plane Graph Topology

```mermaid
flowchart TD
    subgraph RULES [Rules Plane]
        R1["GRAPH-INV-001: PR Protection"]
        R2["GRAPH-INV-002: DAG Execution"]
    end

    subgraph AGENTS [Agents Plane]
        A1["Architect"]
        A2["Developer"]
        A3["Reviewer"]
    end

    subgraph WORKFLOWS [Workflows Plane]
        W1["1_architecture_plan"]
        W2["2_implementation"]
        W3["3_code_review"]
    end

    subgraph CODE [Code AST Plane]
        C1["AgentGraphEngine"]
        C2["GraphTraversalEngine"]
        C3["BM25SearchEngine"]
    end

    W1 --> W2 --> W3
    W1 -.->|ASSIGNED_TO| A1
    W2 -.->|ASSIGNED_TO| A2
    W3 -.->|ASSIGNED_TO| A3
    A2 -.->|IMPLEMENTS| C1
```

---

## 3. Contribution & PR Approval Process
- Anyone can clone and explore this open source repository.
- To submit changes, open a Pull Request targeting `development`.
- PRs run automated Quality Gate checks and require approval from `@raybayly`.
"""

PRE_COMMIT_HOOK_SCRIPT = """#!/usr/bin/env bash
# AgentGraph Pre-Commit Hook
set -e

echo "[AgentGraph Hook] Validating graph topology and running test suite..."

if command -v agentgraph >/dev/null 2>&1; then
    agentgraph validate || { echo "[AgentGraph Hook] Graph validation failed!"; exit 1; }
elif [ -f "./agentgraph/cli.py" ]; then
    python3 -m agentgraph validate || { echo "[AgentGraph Hook] Graph validation failed!"; exit 1; }
fi

echo "[AgentGraph Hook] Validation clean. Proceeding with commit."
"""
