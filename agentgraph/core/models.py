"""Core data models and type definitions for AgentGraph."""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class AgentGraphPlane(str, Enum):
    """Multi-plane separation for heterogeneous agent graph topology."""
    RULES = "rules"          # Directives, policies, invariant rules
    AGENTS = "agents"        # Agent roles, personas, capabilities, authorities
    WORKFLOWS = "workflows"  # Execution DAGs, step sequences, task graphs
    KNOWLEDGE = "knowledge"  # Documents, specifications, domain concepts
    CODE = "code"            # AST modules, classes, functions, code entities


@dataclass
class AgentGraphNode:
    """Atomic entity within the AgentGraph substrate."""
    id: str
    plane: str
    type: str
    label: str
    content: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None
    is_current: bool = True
    created_at: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "plane": self.plane,
            "type": self.type,
            "label": self.label,
            "content": self.content,
            "properties": self.properties,
            "valid_from": self.valid_from,
            "valid_to": self.valid_to,
            "is_current": self.is_current,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AgentGraphNode:
        return cls(
            id=data["id"],
            plane=data.get("plane", AgentGraphPlane.KNOWLEDGE.value),
            type=data.get("type", "node"),
            label=data.get("label", ""),
            content=data.get("content", ""),
            properties=data.get("properties", {}),
            valid_from=data.get("valid_from"),
            valid_to=data.get("valid_to"),
            is_current=data.get("is_current", True),
            created_at=data.get("created_at", datetime.datetime.now(datetime.timezone.utc).isoformat()),
            updated_at=data.get("updated_at", datetime.datetime.now(datetime.timezone.utc).isoformat()),
        )


@dataclass
class AgentGraphEdge:
    """Directed relational link connecting two nodes in AgentGraph."""
    source: str
    target: str
    relation: str
    plane: str
    weight: float = 1.0
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None
    is_current: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "relation": self.relation,
            "plane": self.plane,
            "weight": self.weight,
            "valid_from": self.valid_from,
            "valid_to": self.valid_to,
            "is_current": self.is_current,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AgentGraphEdge:
        return cls(
            source=data["source"],
            target=data["target"],
            relation=data.get("relation", "CONNECTS_TO"),
            plane=data.get("plane", AgentGraphPlane.KNOWLEDGE.value),
            weight=float(data.get("weight", 1.0)),
            valid_from=data.get("valid_from"),
            valid_to=data.get("valid_to"),
            is_current=data.get("is_current", True),
            metadata=data.get("metadata", {}),
        )


@dataclass
class SearchResult:
    """Ranked search result item returned from BM25 lexical graph search."""
    node: AgentGraphNode
    score: float
    matched_plane: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node": self.node.to_dict(),
            "score": self.score,
            "matched_plane": self.matched_plane,
        }


@dataclass
class TraversalPath:
    """Represents a path found between nodes during graph traversal."""
    nodes: List[str]
    edges: List[Dict[str, Any]]
    total_weight: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": self.nodes,
            "edges": self.edges,
            "total_weight": self.total_weight,
            "depth": len(self.nodes) - 1 if self.nodes else 0,
        }


@dataclass
class GraphValidationReport:
    """Topology health audit report for cycles, dangling edges, and isolated nodes."""
    is_valid: bool
    total_nodes: int
    total_edges: int
    plane_counts: Dict[str, int]
    dangling_edges: List[Tuple[str, str]] = field(default_factory=list)
    detected_cycles: List[List[str]] = field(default_factory=list)
    isolated_nodes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "total_nodes": self.total_nodes,
            "total_edges": self.total_edges,
            "plane_counts": self.plane_counts,
            "dangling_edges": self.dangling_edges,
            "detected_cycles": self.detected_cycles,
            "isolated_nodes": self.isolated_nodes,
        }
