import tempfile
import unittest
from pathlib import Path

from agentgraph.init.initializer import RepositoryInitializer
from agentgraph.sync.syncer import RepositorySyncer


class TestRepositorySyncer(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp_dir.name)
        RepositoryInitializer.initialize_repository(target_dir=self.root, install_hooks=False)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_sync_repository(self):
        db_path = self.root / ".agentgraph" / "graph.db"
        graph = RepositorySyncer.sync_repository(root_dir=self.root, db_path=db_path)

        self.assertGreater(len(graph.nodes), 0)
        self.assertGreater(len(graph.edges), 0)
        self.assertTrue(db_path.exists())

        # Check nodes from multiple planes
        planes = set(n.plane for n in graph.nodes.values())
        self.assertIn("agents", planes)
        self.assertIn("workflows", planes)
        self.assertIn("rules", planes)
        self.assertIn("knowledge", planes)


if __name__ == "__main__":
    unittest.main()
