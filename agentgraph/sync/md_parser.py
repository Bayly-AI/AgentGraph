"""Markdown parser for AGENTS.md, documentation hierarchies, and knowledge references."""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Tuple

from agentgraph.core.models import AgentGraphEdge, AgentGraphNode, AgentGraphPlane


class MarkdownParser:
    """Extracts structured agent rules, roles, documents, and cross-links from Markdown files."""

    @staticmethod
    def parse_agents_md(file_path: Path) -> Tuple[List[AgentGraphNode], List[AgentGraphEdge]]:
        """Parse AGENTS.md into node and edge structures."""
        if not file_path.exists():
            return [], []

        content = file_path.read_text(encoding="utf-8", errors="replace")
        nodes: List[AgentGraphNode] = []
        edges: List[AgentGraphEdge] = []

        # 1. Document node
        doc_id = f"doc:{file_path.name}"
        doc_node = AgentGraphNode(
            id=doc_id,
            plane=AgentGraphPlane.KNOWLEDGE.value,
            type="document",
            label=f"Agents Spec ({file_path.name})",
            content=content[:1000],
            properties={"file_path": str(file_path)}
        )
        nodes.append(doc_node)

        # 2. Extract Directives and Rules
        blocks = re.findall(r"(?:###|##|-)\s+\*?\*?([A-Z0-9_\-]+:?\s*.*?)(?=\n(?:###|##|-|\Z))", content, re.DOTALL)
        for idx, block in enumerate(blocks):
            lines = [line.strip() for line in block.strip().split("\n") if line.strip()]
            header = lines[0]
            body = "\n".join(lines[1:]) if len(lines) > 1 else header

            rule_id = f"rule:md_{file_path.stem}_{idx+1}"
            rule_node = AgentGraphNode(
                id=rule_id,
                plane=AgentGraphPlane.RULES.value,
                type="rule_policy",
                label=header[:60],
                content=body,
                properties={
                    "rule_id": rule_id.removeprefix("rule:"),
                    "target_scope": "root"
                }
            )
            nodes.append(rule_node)

            edges.append(AgentGraphEdge(
                source=doc_id,
                target=rule_id,
                relation="DEFINES_RULE",
                plane=AgentGraphPlane.RULES.value
            ))

        # 3. Extract Markdown Cross-Links [Text](link.md)
        links = re.findall(r"\[.*?\]\((.*?\.md)\)", content)
        for link in links:
            target_name = Path(link).name
            edges.append(AgentGraphEdge(
                source=doc_id,
                target=f"doc:{target_name}",
                relation="REFERENCES",
                plane=AgentGraphPlane.KNOWLEDGE.value
            ))

        return nodes, edges

    @staticmethod
    def parse_doc_file(file_path: Path) -> Tuple[AgentGraphNode, List[AgentGraphEdge]]:
        """Parse standard markdown documentation file into Knowledge plane node and reference edges."""
        content = file_path.read_text(encoding="utf-8", errors="replace")
        title = file_path.stem.replace("-", " ").replace("_", " ").title()
        node_id = f"doc:{file_path.name}"

        node = AgentGraphNode(
            id=node_id,
            plane=AgentGraphPlane.KNOWLEDGE.value,
            type="document",
            label=title,
            content=content[:2000],
            properties={"path": str(file_path)}
        )

        edges = []
        for link in re.findall(r"\[.*?\]\((.*?\.md)\)", content):
            target_name = Path(link).name
            edges.append(AgentGraphEdge(
                source=node_id,
                target=f"doc:{target_name}",
                relation="REFERENCES",
                plane=AgentGraphPlane.KNOWLEDGE.value
            ))

        return node, edges
