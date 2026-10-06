import unittest

from agentgraph.core.graph import AgentGraphEngine
from agentgraph.core.models import AgentGraphNode, AgentGraphPlane


class TestBM25Search(unittest.TestCase):
    def setUp(self):
        self.graph = AgentGraphEngine()
        self.graph.add_node(AgentGraphNode(
            id="role:developer",
            plane=AgentGraphPlane.AGENTS.value,
            type="agent_role",
            label="Senior Autonomous Software Developer",
            content="Writes high quality Python code, generates tests, and resolves dependency graph issues."
        ))
        self.graph.add_node(AgentGraphNode(
            id="doc:architecture",
            plane=AgentGraphPlane.KNOWLEDGE.value,
            type="document",
            label="Architecture Overview",
            content="Describes system components, cognitive substrate planes, and graph persistence mechanisms."
        ))

    def test_bm25_query_hits(self):
        results = self.graph.query("software developer python")
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0].node.id, "role:developer")

    def test_bm25_plane_filter(self):
        results = self.graph.query("architecture", plane="knowledge")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].node.id, "doc:architecture")

        results_none = self.graph.query("architecture", plane="agents")
        self.assertEqual(len(results_none), 0)


if __name__ == "__main__":
    unittest.main()
