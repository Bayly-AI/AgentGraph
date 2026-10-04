import tempfile
import unittest
from pathlib import Path

from agentgraph.init.initializer import RepositoryInitializer


class TestRepositoryInitializer(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp_dir.name)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_initialize_layout(self):
        ag_dir = RepositoryInitializer.initialize_repository(target_dir=self.root, install_hooks=False)
        self.assertTrue(ag_dir.exists())
        self.assertTrue((ag_dir / "config.json").exists())
        self.assertTrue((ag_dir / "rules" / "10_core_invariants.json").exists())
        self.assertTrue((ag_dir / "agents" / "developer.json").exists())
        self.assertTrue((ag_dir / "workflows" / "code_review_pipeline.json").exists())
        self.assertTrue((ag_dir / "knowledge" / "architecture.md").exists())
        self.assertTrue((self.root / "AGENTS.md").exists())


if __name__ == "__main__":
    unittest.main()
