"""SQLite persistent storage engine for AgentGraph nodes and edges."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import List, Optional, Tuple

from agentgraph.core.models import AgentGraphEdge, AgentGraphNode


class SQLiteStore:
    """Atomic SQLite storage for AgentGraph cognitive substrate."""

    def __init__(self, db_path: Path | str = ".agentgraph/graph.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        """Create database tables and performance indices."""
        with self._conn:
            self._conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS nodes (
                    id TEXT PRIMARY KEY,
                    plane TEXT NOT NULL,
                    type TEXT NOT NULL,
                    label TEXT NOT NULL,
                    content TEXT NOT NULL,
                    properties TEXT NOT NULL,
                    valid_from TEXT,
                    valid_to TEXT,
                    is_current INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_nodes_plane ON nodes(plane);
                CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(type);

                CREATE TABLE IF NOT EXISTS edges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    target TEXT NOT NULL,
                    relation TEXT NOT NULL,
                    plane TEXT NOT NULL,
                    weight REAL NOT NULL DEFAULT 1.0,
                    valid_from TEXT,
                    valid_to TEXT,
                    is_current INTEGER NOT NULL DEFAULT 1,
                    metadata TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source);
                CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target);
                CREATE INDEX IF NOT EXISTS idx_edges_relation ON edges(relation);
                CREATE INDEX IF NOT EXISTS idx_edges_plane ON edges(plane);
                """
            )

    def upsert_node(self, node: AgentGraphNode) -> None:
        """Insert or update a graph node atomically."""
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO nodes (id, plane, type, label, content, properties, valid_from, valid_to, is_current, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    plane=excluded.plane, type=excluded.type, label=excluded.label,
                    content=excluded.content, properties=excluded.properties,
                    valid_from=excluded.valid_from, valid_to=excluded.valid_to,
                    is_current=excluded.is_current, updated_at=excluded.updated_at
                """,
                (
                    node.id, node.plane, node.type, node.label, node.content,
                    json.dumps(node.properties), node.valid_from, node.valid_to,
                    1 if node.is_current else 0, node.created_at, node.updated_at
                )
            )

    def add_edge(self, edge: AgentGraphEdge) -> None:
        """Insert a relational edge."""
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO edges (source, target, relation, plane, weight, valid_from, valid_to, is_current, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    edge.source, edge.target, edge.relation, edge.plane,
                    edge.weight, edge.valid_from, edge.valid_to,
                    1 if edge.is_current else 0, json.dumps(edge.metadata)
                )
            )

    def clear_edges(self) -> None:
        """Clear all edges prior to graph re-indexing."""
        with self._conn:
            self._conn.execute("DELETE FROM edges;")

    def clear_nodes(self) -> None:
        """Clear all nodes."""
        with self._conn:
            self._conn.execute("DELETE FROM nodes;")

    def clear_all(self) -> None:
        """Clear entire database."""
        with self._conn:
            self._conn.execute("DELETE FROM edges;")
            self._conn.execute("DELETE FROM nodes;")

    def load_all(self) -> Tuple[List[AgentGraphNode], List[AgentGraphEdge]]:
        """Load all nodes and edges from SQLite storage."""
        cursor = self._conn.execute("SELECT * FROM nodes")
        nodes = []
        for row in cursor.fetchall():
            nodes.append(AgentGraphNode(
                id=row["id"], plane=row["plane"], type=row["type"],
                label=row["label"], content=row["content"],
                properties=json.loads(row["properties"]),
                valid_from=row["valid_from"], valid_to=row["valid_to"],
                is_current=bool(row["is_current"]),
                created_at=row["created_at"], updated_at=row["updated_at"]
            ))

        cursor = self._conn.execute("SELECT * FROM edges")
        edges = []
        for row in cursor.fetchall():
            edges.append(AgentGraphEdge(
                source=row["source"], target=row["target"], relation=row["relation"],
                plane=row["plane"], weight=row["weight"],
                valid_from=row["valid_from"], valid_to=row["valid_to"],
                is_current=bool(row["is_current"]),
                metadata=json.loads(row["metadata"])
            ))
        return nodes, edges

    def close(self) -> None:
        """Close SQLite database connection."""
        self._conn.close()
