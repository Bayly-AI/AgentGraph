"""AST and static structure parser for Python and TypeScript/JavaScript codebases."""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import List, Tuple

from agentgraph.core.models import AgentGraphEdge, AgentGraphNode, AgentGraphPlane


class CodeASTParser:
    """Extracts modules, classes, methods, functions, and inheritance links from code files."""

    @staticmethod
    def parse_python_file(file_path: Path) -> Tuple[List[AgentGraphNode], List[AgentGraphEdge]]:
        """Parse Python source code into Code Plane nodes and edges."""
        if not file_path.exists():
            return [], []

        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(content, filename=str(file_path))
        except (SyntaxError, UnicodeDecodeError, OSError, ValueError):
            return [], []

        nodes: List[AgentGraphNode] = []
        edges: List[AgentGraphEdge] = []

        mod_id = f"ast:mod:{file_path.stem}"
        docstring = ast.get_docstring(tree) or ""
        mod_node = AgentGraphNode(
            id=mod_id,
            plane=AgentGraphPlane.CODE.value,
            type="code_module",
            label=f"Module {file_path.name}",
            content=f"Python Module: {file_path.name}\nDocstring: {docstring}",
            properties={"file_path": str(file_path)}
        )
        nodes.append(mod_node)

        for stmt in tree.body:
            if isinstance(stmt, ast.ClassDef):
                cls_id = f"ast:class:{file_path.stem}:{stmt.name}"
                cls_doc = ast.get_docstring(stmt) or ""
                cls_node = AgentGraphNode(
                    id=cls_id,
                    plane=AgentGraphPlane.CODE.value,
                    type="code_class",
                    label=f"Class {stmt.name}",
                    content=f"Class {stmt.name} in {file_path.name}\nDocstring: {cls_doc}",
                    properties={"file_path": str(file_path), "class_name": stmt.name}
                )
                nodes.append(cls_node)
                edges.append(AgentGraphEdge(
                    source=mod_id,
                    target=cls_id,
                    relation="CONTAINS_CLASS",
                    plane=AgentGraphPlane.CODE.value
                ))

                for base in stmt.bases:
                    if isinstance(base, ast.Name):
                        edges.append(AgentGraphEdge(
                            source=cls_id,
                            target=f"ast:class_ref:{base.id}",
                            relation="INHERITS_FROM",
                            plane=AgentGraphPlane.CODE.value
                        ))

                for m_stmt in stmt.body:
                    if isinstance(m_stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        m_id = f"ast:func:{file_path.stem}:{stmt.name}.{m_stmt.name}"
                        m_doc = ast.get_docstring(m_stmt) or ""
                        m_node = AgentGraphNode(
                            id=m_id,
                            plane=AgentGraphPlane.CODE.value,
                            type="code_function",
                            label=f"{stmt.name}.{m_stmt.name}",
                            content=f"Method {m_stmt.name} of class {stmt.name} in {file_path.name}\nDocstring: {m_doc}",
                            properties={"file_path": str(file_path), "class_name": stmt.name, "func_name": m_stmt.name}
                        )
                        nodes.append(m_node)
                        edges.append(AgentGraphEdge(
                            source=cls_id,
                            target=m_id,
                            relation="CONTAINS_METHOD",
                            plane=AgentGraphPlane.CODE.value
                        ))

            elif isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                fn_id = f"ast:func:{file_path.stem}:{stmt.name}"
                fn_doc = ast.get_docstring(stmt) or ""
                fn_node = AgentGraphNode(
                    id=fn_id,
                    plane=AgentGraphPlane.CODE.value,
                    type="code_function",
                    label=f"Function {stmt.name}",
                    content=f"Function {stmt.name} in {file_path.name}\nDocstring: {fn_doc}",
                    properties={"file_path": str(file_path), "func_name": stmt.name}
                )
                nodes.append(fn_node)
                edges.append(AgentGraphEdge(
                    source=mod_id,
                    target=fn_id,
                    relation="CONTAINS_FUNCTION",
                    plane=AgentGraphPlane.CODE.value
                ))

        return nodes, edges

    @staticmethod
    def parse_js_ts_file(file_path: Path) -> Tuple[List[AgentGraphNode], List[AgentGraphEdge]]:
        """Parse JavaScript/TypeScript files into Code Plane nodes and edges."""
        if not file_path.exists():
            return [], []

        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
        except (UnicodeDecodeError, OSError, ValueError):
            return [], []

        nodes: List[AgentGraphNode] = []
        edges: List[AgentGraphEdge] = []

        mod_id = f"ast:mod:{file_path.stem}"
        mod_node = AgentGraphNode(
            id=mod_id,
            plane=AgentGraphPlane.CODE.value,
            type="code_module",
            label=f"Module {file_path.name}",
            content=f"JS/TS Module: {file_path.name}\nSize: {len(content)} chars",
            properties={"file_path": str(file_path)}
        )
        nodes.append(mod_node)

        # Extract classes (class Foo or export class Foo)
        class_matches = re.finditer(r"(?:export\s+)?class\s+([A-Za-z0-9_$]+)(?:\s+extends\s+([A-Za-z0-9_$]+))?", content)
        for m in class_matches:
            cls_name = m.group(1)
            parent_cls = m.group(2)
            cls_id = f"ast:class:{file_path.stem}:{cls_name}"
            nodes.append(AgentGraphNode(
                id=cls_id,
                plane=AgentGraphPlane.CODE.value,
                type="code_class",
                label=f"Class {cls_name}",
                content=f"Class {cls_name} in {file_path.name}",
                properties={"file_path": str(file_path), "class_name": cls_name}
            ))
            edges.append(AgentGraphEdge(
                source=mod_id,
                target=cls_id,
                relation="CONTAINS_CLASS",
                plane=AgentGraphPlane.CODE.value
            ))
            if parent_cls:
                edges.append(AgentGraphEdge(
                    source=cls_id,
                    target=f"ast:class_ref:{parent_cls}",
                    relation="INHERITS_FROM",
                    plane=AgentGraphPlane.CODE.value
                ))

        # Extract functions
        func_matches = re.finditer(r"(?:export\s+)?(?:async\s+)?function\s+([A-Za-z0-9_$]+)\s*\(", content)
        for m in func_matches:
            fn_name = m.group(1)
            fn_id = f"ast:func:{file_path.stem}:{fn_name}"
            nodes.append(AgentGraphNode(
                id=fn_id,
                plane=AgentGraphPlane.CODE.value,
                type="code_function",
                label=f"Function {fn_name}",
                content=f"Function {fn_name} in {file_path.name}",
                properties={"file_path": str(file_path), "func_name": fn_name}
            ))
            edges.append(AgentGraphEdge(
                source=mod_id,
                target=fn_id,
                relation="CONTAINS_FUNCTION",
                plane=AgentGraphPlane.CODE.value
            ))

        return nodes, edges
