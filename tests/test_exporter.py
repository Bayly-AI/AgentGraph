import unittest

from agentgraph.core.graph import AgentGraphEngine
from agentgraph.core.models import AgentGraphEdge, AgentGraphNode
from agentgraph.export.exporter import GraphExporter


class TestGraphExporter(unittest.TestCase):
    def setUp(self):
        self.graph = AgentGraphEngine()
        self.graph.add_node(AgentGraphNode(id="role:architect", plane="agents", type="agent_role", label="Architect"))
        self.graph.add_node(AgentGraphNode(id="step:1", plane="workflows", type="step", label="Design"))
        self.graph.add_edge(AgentGraphEdge(source="step:1", target="role:architect", relation="ASSIGNED_TO", plane="workflows"))

    def test_export_json(self):
        json_str = GraphExporter.to_json(self.graph)
        self.assertIn("role:architect", json_str)
        self.assertIn("ASSIGNED_TO", json_str)

    def test_export_mermaid(self):
        mermaid_str = GraphExporter.to_mermaid(self.graph)
        self.assertIn("flowchart", mermaid_str)
        self.assertIn("subgraph AGENTS", mermaid_str)
        self.assertIn("ASSIGNED_TO", mermaid_str)

    def test_export_dot(self):
        dot_str = GraphExporter.to_dot(self.graph)
        self.assertIn("digraph AgentGraph", dot_str)
        self.assertIn("ASSIGNED_TO", dot_str)


if __name__ == "__main__":
    unittest.main()
