import unittest

from agentgraph.core.graph import AgentGraphEngine
from agentgraph.core.models import AgentGraphEdge, AgentGraphNode, AgentGraphPlane


class TestGraphTraversal(unittest.TestCase):
    def setUp(self):
        self.graph = AgentGraphEngine()

        # Build DAG: A -> B -> C -> D
        #               A -> D
        for name in ["A", "B", "C", "D"]:
            self.graph.add_node(AgentGraphNode(
                id=name,
                plane=AgentGraphPlane.WORKFLOWS.value,
                type="step",
                label=f"Step {name}"
            ))

        self.graph.add_edge(AgentGraphEdge(source="A", target="B", relation="DEPENDS_ON", plane="workflows"))
        self.graph.add_edge(AgentGraphEdge(source="B", target="C", relation="DEPENDS_ON", plane="workflows"))
        self.graph.add_edge(AgentGraphEdge(source="C", target="D", relation="DEPENDS_ON", plane="workflows"))
        self.graph.add_edge(AgentGraphEdge(source="A", target="D", relation="DEPENDS_ON", plane="workflows"))

    def test_bfs_traversal(self):
        hops = self.graph.traverse(start_node_id="A", direction="outgoing", max_depth=2)
        node_ids = [h["node_id"] for h in hops]
        self.assertIn("B", node_ids)
        self.assertIn("D", node_ids)
        self.assertIn("C", node_ids)

    def test_find_paths(self):
        paths = self.graph.find_paths("A", "D")
        self.assertEqual(len(paths), 2)
        node_sequences = [p.nodes for p in paths]
        self.assertIn(["A", "B", "C", "D"], node_sequences)
        self.assertIn(["A", "D"], node_sequences)

    def test_resolve_dependencies(self):
        deps = self.graph.resolve_dependencies("A")
        # All reachable dependencies resolved
        self.assertIn("B", deps)
        self.assertIn("C", deps)
        self.assertIn("D", deps)

    def test_topological_sort(self):
        sorted_nodes, has_cycle = self.graph.topological_sort()
        self.assertFalse(has_cycle)
        self.assertEqual(len(sorted_nodes), 4)
        self.assertLess(sorted_nodes.index("A"), sorted_nodes.index("B"))
        self.assertLess(sorted_nodes.index("B"), sorted_nodes.index("C"))

    def test_cycle_detection(self):
        # Introduce cycle: D -> A
        self.graph.add_edge(AgentGraphEdge(source="D", target="A", relation="DEPENDS_ON", plane="workflows"))
        report = self.graph.validate()
        self.assertFalse(report.is_valid)
        self.assertGreater(len(report.detected_cycles), 0)


if __name__ == "__main__":
    unittest.main()
