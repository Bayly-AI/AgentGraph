"""Graph traversal, pathfinding, dependency resolution, and topological analysis."""

from __future__ import annotations

from collections import deque
from typing import Dict, List, Optional, Set, Tuple

from agentgraph.core.models import AgentGraphEdge, AgentGraphNode, TraversalPath


class GraphTraversalEngine:
    """Provides high-performance graph traversal algorithms across multi-plane agent networks."""

    @staticmethod
    def bfs_traverse(
        start_node_id: str,
        outgoing_edges: Dict[str, List[AgentGraphEdge]],
        incoming_edges: Dict[str, List[AgentGraphEdge]],
        direction: str = "outgoing",
        max_depth: int = 3,
        relation_filter: Optional[str] = None,
        plane_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Traverse graph using Breadth-First Search up to max_depth.
        Returns visited nodes along with hop distance and traversed edge.
        """
        visited: Set[str] = {start_node_id}
        queue = deque([(start_node_id, 0, None)])
        results: List[Dict[str, Any]] = []

        while queue:
            curr_node_id, depth, edge_used = queue.popleft()

            if curr_node_id != start_node_id:
                results.append({
                    "node_id": curr_node_id,
                    "depth": depth,
                    "edge": edge_used.to_dict() if edge_used else None,
                })

            if depth >= max_depth:
                continue

            candidate_edges: List[AgentGraphEdge] = []
            if direction in ("outgoing", "both"):
                candidate_edges.extend(outgoing_edges.get(curr_node_id, []))
            if direction in ("incoming", "both"):
                candidate_edges.extend(incoming_edges.get(curr_node_id, []))

            for edge in candidate_edges:
                if relation_filter and edge.relation != relation_filter:
                    continue
                if plane_filter and edge.plane != plane_filter:
                    continue

                neighbor_id = edge.target if edge.source == curr_node_id else edge.source
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append((neighbor_id, depth + 1, edge))

        return results

    @staticmethod
    def find_paths(
        source_id: str,
        target_id: str,
        outgoing_edges: Dict[str, List[AgentGraphEdge]],
        max_depth: int = 6
    ) -> List[TraversalPath]:
        """Find all acyclic paths between source_id and target_id up to max_depth."""
        all_paths: List[TraversalPath] = []

        def dfs(current: str, target: str, visited: Set[str], current_nodes: List[str], current_edges: List[AgentGraphEdge], total_weight: float, depth: int):
            if current == target:
                all_paths.append(TraversalPath(
                    nodes=list(current_nodes),
                    edges=[e.to_dict() for e in current_edges],
                    total_weight=total_weight
                ))
                return

            if depth >= max_depth:
                return

            for edge in outgoing_edges.get(current, []):
                next_node = edge.target
                if next_node not in visited:
                    visited.add(next_node)
                    current_nodes.append(next_node)
                    current_edges.append(edge)

                    dfs(next_node, target, visited, current_nodes, current_edges, total_weight + edge.weight, depth + 1)

                    current_edges.pop()
                    current_nodes.pop()
                    visited.remove(next_node)

        dfs(source_id, target_id, {source_id}, [source_id], [], 0.0, 0)
        return all_paths

    @staticmethod
    def resolve_dependencies(
        node_id: str,
        outgoing_edges: Dict[str, List[AgentGraphEdge]],
        dependency_relations: Optional[Set[str]] = None
    ) -> List[str]:
        """
        Recursively resolve all downstream dependencies in topological order.
        Default dependency relations: {'DEPENDS_ON', 'REQUIRES', 'INHERITS_FROM', 'IMPORTS', 'CALLS'}
        """
        if dependency_relations is None:
            dependency_relations = {"DEPENDS_ON", "REQUIRES", "INHERITS_FROM", "IMPORTS", "CALLS"}

        visited: Set[str] = set()
        order: List[str] = []

        def dfs(curr: str):
            visited.add(curr)
            for edge in outgoing_edges.get(curr, []):
                if edge.relation in dependency_relations:
                    if edge.target not in visited:
                        dfs(edge.target)
            order.append(curr)

        dfs(node_id)
        # Reverse to get topological dependency resolution order (root dependencies first)
        return [n for n in reversed(order) if n != node_id]

    @staticmethod
    def topological_sort(
        nodes: Dict[str, AgentGraphNode],
        outgoing_edges: Dict[str, List[AgentGraphEdge]],
        plane: Optional[str] = None
    ) -> Tuple[List[str], bool]:
        """
        Computes topological ordering using Kahn's algorithm.
        Returns (sorted_node_ids, has_cycle).
        """
        target_nodes = {k: v for k, v in nodes.items() if (plane is None or v.plane == plane)}
        in_degree: Dict[str, int] = {k: 0 for k in target_nodes}

        for src, edges in outgoing_edges.items():
            if src in target_nodes:
                for e in edges:
                    if e.target in in_degree:
                        in_degree[e.target] += 1

        queue = deque([n for n, deg in in_degree.items() if deg == 0])
        sorted_order: List[str] = []

        while queue:
            curr = queue.popleft()
            sorted_order.append(curr)

            for e in outgoing_edges.get(curr, []):
                if e.target in in_degree:
                    in_degree[e.target] -= 1
                    if in_degree[e.target] == 0:
                        queue.append(e.target)

        has_cycle = len(sorted_order) < len(target_nodes)
        return sorted_order, has_cycle

    @staticmethod
    def detect_cycles(
        nodes: Dict[str, AgentGraphNode],
        outgoing_edges: Dict[str, List[AgentGraphEdge]],
        plane: Optional[str] = None
    ) -> List[List[str]]:
        """Detect all cycle loops in graph using DFS with recursion stack."""
        target_nodes = {k: v for k, v in nodes.items() if (plane is None or v.plane == plane)}
        visited: Set[str] = set()
        stack: Set[str] = set()
        cycles: List[List[str]] = []

        def dfs(curr: str, path: List[str]):
            visited.add(curr)
            stack.add(curr)
            path.append(curr)

            for edge in outgoing_edges.get(curr, []):
                target = edge.target
                if target in target_nodes:
                    if target not in visited:
                        dfs(target, path)
                    elif target in stack:
                        start_idx = path.index(target)
                        cycles.append(path[start_idx:] + [target])

            path.pop()
            stack.remove(curr)

        for n_id in target_nodes:
            if n_id not in visited:
                dfs(n_id, [])

        return cycles
