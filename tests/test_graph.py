import tempfile
import unittest
from pathlib import Path

from agentgraph.core.graph import AgentGraphEngine
from agentgraph.core.models import AgentGraphEdge, AgentGraphNode, AgentGraphPlane


class TestAgentGraphEngine(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp_dir.name) / "test_graph.db"
        self.graph = AgentGraphEngine(db_path=self.db_path)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_add_and_retrieve_nodes(self):
        node = AgentGraphNode(
            id="role:architect",
            plane=AgentGraphPlane.AGENTS.value,
            type="agent_role",
            label="System Architect",
            content="Designs system graphs and execution topologies."
        )
        self.graph.add_node(node)

        retrieved = self.graph.get_node("role:architect")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.label, "System Architect")
        self.assertEqual(retrieved.plane, AgentGraphPlane.AGENTS.value)

    def test_add_and_retrieve_edges(self):
        n1 = AgentGraphNode(id="step:1", plane=AgentGraphPlane.WORKFLOWS.value, type="step", label="Step 1")
        n2 = AgentGraphNode(id="step:2", plane=AgentGraphPlane.WORKFLOWS.value, type="step", label="Step 2")
        self.graph.add_node(n1)
        self.graph.add_node(n2)

        edge = AgentGraphEdge(
            source="step:2",
            target="step:1",
            relation="DEPENDS_ON",
            plane=AgentGraphPlane.WORKFLOWS.value
        )
        self.graph.add_edge(edge)

        outgoing = self.graph.get_outgoing("step:2")
        self.assertEqual(len(outgoing), 1)
        self.assertEqual(outgoing[0].target, "step:1")

        incoming = self.graph.get_incoming("step:1")
        self.assertEqual(len(incoming), 1)
        self.assertEqual(incoming[0].source, "step:2")

    def test_persistence_sqlite(self):
        n1 = AgentGraphNode(id="doc:arch", plane=AgentGraphPlane.KNOWLEDGE.value, type="document", label="Arch Doc")
        self.graph.add_node(n1)
        self.graph.save_to_db()

        new_graph = AgentGraphEngine(db_path=self.db_path)
        new_graph.load_from_db()

        self.assertIn("doc:arch", new_graph.nodes)
        self.assertEqual(new_graph.nodes["doc:arch"].label, "Arch Doc")

    def test_stats(self):
        n1 = AgentGraphNode(id="node:1", plane=AgentGraphPlane.CODE.value, type="code_class", label="Class 1")
        n2 = AgentGraphNode(id="node:2", plane=AgentGraphPlane.CODE.value, type="code_class", label="Class 2")
        self.graph.add_node(n1)
        self.graph.add_node(n2)
        self.graph.add_edge(AgentGraphEdge(source="node:1", target="node:2", relation="INHERITS_FROM", plane="code"))

        stats = self.graph.get_stats()
        self.assertEqual(stats["total_nodes"], 2)
        self.assertEqual(stats["total_edges"], 1)
        self.assertEqual(stats["plane_node_distribution"]["code"], 2)


if __name__ == "__main__":
    unittest.main()
