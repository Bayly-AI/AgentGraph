"""Exporters for visualizing and serializing AgentGraph to Mermaid, Graphviz DOT, and JSON."""

from __future__ import annotations

import json
from typing import Dict, List, Optional

from agentgraph.core.graph import AgentGraphEngine


class GraphExporter:
    """Exports AgentGraph topologies into various serialization and visual diagram formats."""

    @staticmethod
    def to_json(graph: AgentGraphEngine, indent: int = 2) -> str:
        """Export full graph structure to JSON."""
        data = {
            "nodes": [n.to_dict() for n in graph.nodes.values()],
            "edges": [e.to_dict() for e in graph.edges],
            "stats": graph.get_stats(),
        }
        return json.dumps(data, indent=indent)

    @staticmethod
    def to_mermaid(
        graph: AgentGraphEngine,
        plane: Optional[str] = None,
        direction: str = "TD"
    ) -> str:
        """
        Export graph or single plane into Mermaid graph syntax (flowchart TD / LR).
        """
        lines = [f"flowchart {direction}"]

        # Filter nodes
        filtered_nodes = {
            nid: n for nid, n in graph.nodes.items()
            if (plane is None or n.plane == plane)
        }

        # Subgraphs per plane
        nodes_by_plane: Dict[str, List[str]] = {}
        for nid, n in filtered_nodes.items():
            nodes_by_plane.setdefault(n.plane, []).append(nid)

        for p_name, nids in sorted(nodes_by_plane.items()):
            lines.append(f"    subgraph {p_name.upper()} [Plane: {p_name.capitalize()}]")
            for nid in nids:
                node = filtered_nodes[nid]
                clean_id = nid.replace(":", "_").replace("-", "_").replace(".", "_")
                clean_label = node.label.replace('"', "'")
                lines.append(f'        {clean_id}["{clean_label}"]')
            lines.append("    end")

        # Edges
        for e in graph.edges:
            if e.source in filtered_nodes and e.target in filtered_nodes:
                src_clean = e.source.replace(":", "_").replace("-", "_").replace(".", "_")
                tgt_clean = e.target.replace(":", "_").replace("-", "_").replace(".", "_")
                rel_clean = e.relation.replace('"', "")
                lines.append(f'    {src_clean} -->|"{rel_clean}"| {tgt_clean}')

        return "\n".join(lines)

    @staticmethod
    def to_dot(graph: AgentGraphEngine, plane: Optional[str] = None) -> str:
        """Export graph to Graphviz DOT format."""
        lines = ["digraph AgentGraph {", "    rankdir=LR;", "    node [shape=box, style=rounded, fontname=Helvetica];"]

        filtered_nodes = {
            nid: n for nid, n in graph.nodes.items()
            if (plane is None or n.plane == plane)
        }

        for nid, n in filtered_nodes.items():
            clean_id = nid.replace(":", "_").replace("-", "_").replace(".", "_")
            label = f"{n.label}\\n({n.plane}:{n.type})"
            lines.append(f'    "{clean_id}" [label="{label}"];')

        for e in graph.edges:
            if e.source in filtered_nodes and e.target in filtered_nodes:
                src_clean = e.source.replace(":", "_").replace("-", "_").replace(".", "_")
                tgt_clean = e.target.replace(":", "_").replace("-", "_").replace(".", "_")
                lines.append(f'    "{src_clean}" -> "{tgt_clean}" [label="{e.relation}"];')

        lines.append("}")
        return "\n".join(lines)
