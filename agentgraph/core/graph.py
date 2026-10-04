"""Main in-memory and persisted Graph engine for AgentGraph."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from agentgraph.core.models import (
    AgentGraphEdge,
    AgentGraphNode,
    AgentGraphPlane,
    GraphValidationReport,
    SearchResult,
    TraversalPath,
)
from agentgraph.core.search import BM25SearchEngine
from agentgraph.core.storage import SQLiteStore
from agentgraph.core.traversal import GraphTraversalEngine


class AgentGraphEngine:
    """High-performance multi-plane Graph Engine for AI agents, workflows, and codebases."""

    def __init__(self, db_path: Path | str = ".agentgraph/graph.db") -> None:
        self.db_path = Path(db_path)
        self.nodes: Dict[str, AgentGraphNode] = {}
        self.edges: List[AgentGraphEdge] = []
        self._outgoing: Dict[str, List[AgentGraphEdge]] = defaultdict(list)
        self._incoming: Dict[str, List[AgentGraphEdge]] = defaultdict(list)
        self.search_engine = BM25SearchEngine()

    # -------------------------------------------------------------------------
    # Node & Edge Mutators
    # -------------------------------------------------------------------------

    def add_node(self, node: AgentGraphNode) -> None:
        """Add or update a node in the graph and update search index."""
        self.nodes[node.id] = node
        self.search_engine.index_node(node)

    def add_edge(self, edge: AgentGraphEdge) -> None:
        """Add a directed relational edge between nodes."""
        self.edges.append(edge)
        self._outgoing[edge.source].append(edge)
        self._incoming[edge.target].append(edge)

    def get_node(self, node_id: str) -> Optional[AgentGraphNode]:
        """Fetch node by unique ID."""
        return self.nodes.get(node_id)

    def get_outgoing(self, source_id: str, relation: Optional[str] = None) -> List[AgentGraphEdge]:
        """Fetch outgoing edges originating from source_id."""
        edges = self._outgoing.get(source_id, [])
        return [e for e in edges if e.relation == relation] if relation else list(edges)

    def get_incoming(self, target_id: str, relation: Optional[str] = None) -> List[AgentGraphEdge]:
        """Fetch incoming edges pointing to target_id."""
        edges = self._incoming.get(target_id, [])
        return [e for e in edges if e.relation == relation] if relation else list(edges)

    def get_neighbors(self, node_id: str, direction: str = "both") -> List[str]:
        """Fetch adjacent neighbor node IDs."""
        neighbors: Set[str] = set()
        if direction in ("outgoing", "both"):
            for e in self._outgoing.get(node_id, []):
                neighbors.add(e.target)
        if direction in ("incoming", "both"):
            for e in self._incoming.get(node_id, []):
                neighbors.add(e.source)
        return sorted(neighbors)

    def clear(self) -> None:
        """Reset in-memory graph structures."""
        self.nodes.clear()
        self.edges.clear()
        self._outgoing.clear()
        self._incoming.clear()
        self.search_engine.clear()

    # -------------------------------------------------------------------------
    # Search & Traversal
    # -------------------------------------------------------------------------

    def query(
        self,
        query_str: str,
        plane: Optional[str] = None,
        limit: int = 10
    ) -> List[SearchResult]:
        """Perform fast BM25 lexical search across graph nodes."""
        return self.search_engine.query(query_str=query_str, target_plane=plane, limit=limit)

    def traverse(
        self,
        start_node_id: str,
        direction: str = "outgoing",
        max_depth: int = 3,
        relation_filter: Optional[str] = None,
        plane_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Perform Breadth-First Search traversal from start_node_id."""
        return GraphTraversalEngine.bfs_traverse(
            start_node_id=start_node_id,
            outgoing_edges=self._outgoing,
            incoming_edges=self._incoming,
            direction=direction,
            max_depth=max_depth,
            relation_filter=relation_filter,
            plane_filter=plane_filter,
        )

    def find_paths(self, source_id: str, target_id: str, max_depth: int = 6) -> List[TraversalPath]:
        """Find all acyclic paths between source_id and target_id."""
        return GraphTraversalEngine.find_paths(
            source_id=source_id,
            target_id=target_id,
            outgoing_edges=self._outgoing,
            max_depth=max_depth,
        )

    def resolve_dependencies(self, node_id: str) -> List[str]:
        """Topologically resolve all upstream/downstream dependencies of a node."""
        return GraphTraversalEngine.resolve_dependencies(
            node_id=node_id,
            outgoing_edges=self._outgoing,
        )

    def topological_sort(self, plane: Optional[str] = None) -> Tuple[List[str], bool]:
        """Compute topological sort ordering. Returns (sorted_ids, has_cycle)."""
        return GraphTraversalEngine.topological_sort(
            nodes=self.nodes,
            outgoing_edges=self._outgoing,
            plane=plane,
        )

    # -------------------------------------------------------------------------
    # Validation & Topology Analysis
    # -------------------------------------------------------------------------

    def validate(self) -> GraphValidationReport:
        """Audit graph topology for cycle dependencies, dangling edges, and isolated nodes."""
        plane_counts = Counter(n.plane for n in self.nodes.values())
        dangling_edges: List[Tuple[str, str]] = []

        for e in self.edges:
            if e.source not in self.nodes:
                dangling_edges.append((e.source, e.target))
            elif (
                not e.target.startswith("tool:")
                and not e.target.startswith("ast:class_ref:")
                and not e.target.startswith("external:")
                and e.target not in self.nodes
            ):
                dangling_edges.append((e.source, e.target))

        cycles = GraphTraversalEngine.detect_cycles(
            nodes=self.nodes,
            outgoing_edges=self._outgoing,
        )

        connected_nodes = set(self._outgoing.keys()) | set(self._incoming.keys())
        isolated_nodes = [nid for nid in self.nodes if nid not in connected_nodes]

        is_valid = (len(dangling_edges) == 0 and len(cycles) == 0)

        return GraphValidationReport(
            is_valid=is_valid,
            total_nodes=len(self.nodes),
            total_edges=len(self.edges),
            plane_counts=dict(plane_counts),
            dangling_edges=dangling_edges,
            detected_cycles=cycles,
            isolated_nodes=isolated_nodes,
        )

    def get_stats(self) -> Dict[str, Any]:
        """Return topological summary statistics across all planes."""
        plane_node_counts = Counter(n.plane for n in self.nodes.values())
        plane_edge_counts = Counter(e.plane for e in self.edges)
        relation_counts = Counter(e.relation for e in self.edges)
        type_counts = Counter(n.type for n in self.nodes.values())

        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "plane_node_distribution": dict(plane_node_counts),
            "plane_edge_distribution": dict(plane_edge_counts),
            "relation_distribution": dict(relation_counts),
            "node_type_distribution": dict(type_counts),
        }

    # -------------------------------------------------------------------------
    # Persistence
    # -------------------------------------------------------------------------

    def save_to_db(self) -> None:
        """Persist in-memory graph to SQLite database."""
        store = SQLiteStore(self.db_path)
        store.clear_all()
        for node in self.nodes.values():
            store.upsert_node(node)
        for edge in self.edges:
            store.add_edge(edge)
        store.close()

    def load_from_db(self) -> None:
        """Load graph nodes and edges from SQLite database."""
        store = SQLiteStore(self.db_path)
        self.clear()
        nodes, edges = store.load_all()
        for node in nodes:
            self.add_node(node)
        for edge in edges:
            self.add_edge(edge)
        store.close()

    @classmethod
    def init(cls, workspace_dir: Path | str = ".", no_hooks: bool = False) -> "AgentGraphEngine":
        """Initialize workspace directory layout (.agentgraph/, AGENTS.md, git hooks) and sync substrate."""
        from agentgraph.init.initializer import RepositoryInitializer
        from agentgraph.sync.syncer import RepositorySyncer

        target_dir = Path(workspace_dir)
        RepositoryInitializer.initialize_repository(target_dir=target_dir, install_hooks=not no_hooks)
        graph = RepositorySyncer.sync_repository(root_dir=target_dir)
        return graph


# Primary class alias
AgentGraph = AgentGraphEngine
