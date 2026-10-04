"""Workspace file system crawler and graph synchronization engine."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from agentgraph.core.graph import AgentGraphEngine
from agentgraph.core.models import AgentGraphEdge, AgentGraphNode, AgentGraphPlane
from agentgraph.sync.code_parser import CodeASTParser
from agentgraph.sync.md_parser import MarkdownParser


class RepositorySyncer:
    """Discovers repository artifacts and synchronizes them into the AgentGraph database."""

    @classmethod
    def sync_repository(cls, root_dir: Path | str = ".", db_path: Path | str = ".agentgraph/graph.db") -> AgentGraphEngine:
        """Scan workspace, build in-memory graph, persist to SQLite, and return populated engine."""
        root = Path(root_dir).resolve()
        graph = AgentGraphEngine(db_path=db_path)
        graph.clear()

        # 1. Ingest AGENTS.md
        agents_md = root / "AGENTS.md"
        if agents_md.exists():
            nodes, edges = MarkdownParser.parse_agents_md(agents_md)
            for n in nodes:
                graph.add_node(n)
            for e in edges:
                graph.add_edge(e)

        # 2. Ingest Rules in .agentgraph/rules/*.json
        rules_dir = root / ".agentgraph" / "rules"
        if rules_dir.exists():
            for rule_file in sorted(rules_dir.glob("*.json")):
                try:
                    rule_data = json.loads(rule_file.read_text(encoding="utf-8"))
                    items = rule_data if isinstance(rule_data, list) else [rule_data]
                    for item in items:
                        r_id = f"rule:{item.get('id', rule_file.stem)}"
                        node = AgentGraphNode(
                            id=r_id,
                            plane=AgentGraphPlane.RULES.value,
                            type="rule_policy",
                            label=item.get("title", item.get("id", rule_file.stem)),
                            content=item.get("content", ""),
                            properties=item
                        )
                        graph.add_node(node)

                        for role_id in item.get("governs_roles", []):
                            target_role = role_id if role_id.startswith("role:") else f"role:{role_id}"
                            graph.add_edge(AgentGraphEdge(
                                source=r_id,
                                target=target_role,
                                relation="GOVERNS",
                                plane=AgentGraphPlane.RULES.value
                            ))
                except Exception:
                    pass

        # 3. Ingest Agents in .agentgraph/agents/*.json
        agents_dir = root / ".agentgraph" / "agents"
        if agents_dir.exists():
            for agent_file in sorted(agents_dir.glob("*.json")):
                try:
                    agent_data = json.loads(agent_file.read_text(encoding="utf-8"))
                    role_id = f"role:{agent_data.get('role_id', agent_file.stem)}"
                    role_node = AgentGraphNode(
                        id=role_id,
                        plane=AgentGraphPlane.AGENTS.value,
                        type="agent_role",
                        label=agent_data.get("name", agent_file.stem),
                        content=agent_data.get("description", ""),
                        properties=agent_data
                    )
                    graph.add_node(role_node)

                    # Tools edges
                    for tool in agent_data.get("tools", []):
                        graph.add_edge(AgentGraphEdge(
                            source=role_id,
                            target=f"tool:{tool}",
                            relation="CAN_USE_TOOL",
                            plane=AgentGraphPlane.AGENTS.value
                        ))

                    # Parent inheritance
                    if agent_data.get("parent_role_id"):
                        parent_id = agent_data["parent_role_id"]
                        formatted_parent = parent_id if parent_id.startswith("role:") else f"role:{parent_id}"
                        graph.add_edge(AgentGraphEdge(
                            source=role_id,
                            target=formatted_parent,
                            relation="INHERITS_FROM",
                            plane=AgentGraphPlane.AGENTS.value
                        ))
                except Exception:
                    pass

        # 4. Ingest Workflows in .agentgraph/workflows/*.json
        workflows_dir = root / ".agentgraph" / "workflows"
        if workflows_dir.exists():
            for wf_file in sorted(workflows_dir.glob("*.json")):
                try:
                    wf_data = json.loads(wf_file.read_text(encoding="utf-8"))
                    wf_id = f"workflow:{wf_data.get('id', wf_file.stem)}"
                    wf_node = AgentGraphNode(
                        id=wf_id,
                        plane=AgentGraphPlane.WORKFLOWS.value,
                        type="workflow_dag",
                        label=wf_data.get("name", wf_file.stem),
                        content=wf_data.get("description", ""),
                        properties=wf_data
                    )
                    graph.add_node(wf_node)

                    for step in wf_data.get("steps", []):
                        step_id = f"step:{wf_data.get('id', wf_file.stem)}:{step.get('id')}"
                        step_node = AgentGraphNode(
                            id=step_id,
                            plane=AgentGraphPlane.WORKFLOWS.value,
                            type="workflow_step",
                            label=step.get("name", step.get("id")),
                            content=step.get("description", ""),
                            properties=step
                        )
                        graph.add_node(step_node)
                        graph.add_edge(AgentGraphEdge(
                            source=wf_id,
                            target=step_id,
                            relation="CONTAINS_STEP",
                            plane=AgentGraphPlane.WORKFLOWS.value
                        ))

                        if step.get("agent_role"):
                            role_target = step["agent_role"] if step["agent_role"].startswith("role:") else f"role:{step['agent_role']}"
                            graph.add_edge(AgentGraphEdge(
                                source=step_id,
                                target=role_target,
                                relation="ASSIGNED_TO",
                                plane=AgentGraphPlane.WORKFLOWS.value
                            ))

                        for dep in step.get("depends_on", []):
                            dep_step_id = f"step:{wf_data.get('id', wf_file.stem)}:{dep}"
                            graph.add_edge(AgentGraphEdge(
                                source=step_id,
                                target=dep_step_id,
                                relation="DEPENDS_ON",
                                plane=AgentGraphPlane.WORKFLOWS.value
                            ))
                except Exception:
                    pass

        # 5. Ingest Knowledge & Documentation
        doc_dirs = [root / "docs", root / ".agentgraph" / "knowledge"]
        for d in doc_dirs:
            if d.exists():
                for doc_file in d.rglob("*.md"):
                    try:
                        node, edges = MarkdownParser.parse_doc_file(doc_file)
                        graph.add_node(node)
                        for e in edges:
                            graph.add_edge(e)
                    except Exception:
                        pass

        # 6. Ingest Python Code AST
        src_dirs = [root / "agentgraph", root / "src"]
        for s_dir in src_dirs:
            if s_dir.exists():
                for py_file in s_dir.rglob("*.py"):
                    if py_file.name.startswith("__pycache__"):
                        continue
                    try:
                        nodes, edges = CodeASTParser.parse_python_file(py_file)
                        for n in nodes:
                            graph.add_node(n)
                        for e in edges:
                            graph.add_edge(e)
                    except Exception:
                        pass

        # 7. Ingest JS / TS Code
        js_dirs = [root / "packages", root / "src"]
        for j_dir in js_dirs:
            if j_dir.exists():
                for code_file in j_dir.rglob("*.ts"):
                    if "node_modules" in str(code_file) or "dist" in str(code_file):
                        continue
                    try:
                        nodes, edges = CodeASTParser.parse_js_ts_file(code_file)
                        for n in nodes:
                            graph.add_node(n)
                        for e in edges:
                            graph.add_edge(e)
                    except Exception:
                        pass

        # Persist to SQLite
        graph.save_to_db()
        return graph
