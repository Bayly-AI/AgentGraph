"""AgentGraph: Multi-Plane Cognitive Substrate & Knowledge Graph Engine for AI Agents."""

from agentgraph.core.graph import AgentGraph, AgentGraphEngine
from agentgraph.core.models import (
    AgentGraphEdge,
    AgentGraphNode,
    AgentGraphPlane,
    GraphValidationReport,
    SearchResult,
    TraversalPath,
)
from agentgraph.export.exporter import GraphExporter
from agentgraph.init.initializer import RepositoryInitializer
from agentgraph.sync.syncer import RepositorySyncer

__version__ = "1.0.0"
__author__ = "Ray Bayly"
__license__ = "Apache-2.0"

__all__ = [
    "AgentGraph",
    "AgentGraphEngine",
    "AgentGraphNode",
    "AgentGraphEdge",
    "AgentGraphPlane",
    "SearchResult",
    "TraversalPath",
    "GraphValidationReport",
    "RepositorySyncer",
    "RepositoryInitializer",
    "GraphExporter",
]
