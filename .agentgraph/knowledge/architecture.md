# System Architecture & Graph Topology

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
