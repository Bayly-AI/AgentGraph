import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

from agentgraph.cli import main
from agentgraph.init.initializer import RepositoryInitializer


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp_dir.name)
        RepositoryInitializer.initialize_repository(target_dir=self.root, install_hooks=False)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def _run_cli(self, args: list[str]) -> str:
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            main(args)
            return sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout

    def test_cli_init_and_sync(self):
        out = self._run_cli(["sync", "--dir", str(self.root), "--db", str(self.root / "test.db")])
        self.assertIn("Sync complete", out)

    def test_cli_query(self):
        db_path = str(self.root / ".agentgraph" / "graph.db")
        self._run_cli(["sync", "--dir", str(self.root), "--db", db_path])
        out = self._run_cli(["query", "architect", "--db", db_path, "--json"])
        results = json.loads(out)
        self.assertIsInstance(results, list)

    def test_cli_validate(self):
        db_path = str(self.root / ".agentgraph" / "graph.db")
        out = self._run_cli(["validate", "--dir", str(self.root), "--db", db_path, "--json"])
        rep = json.loads(out)
        self.assertTrue(rep["is_valid"])

    def test_cli_stats(self):
        db_path = str(self.root / ".agentgraph" / "graph.db")
        self._run_cli(["sync", "--dir", str(self.root), "--db", db_path])
        out = self._run_cli(["stats", "--db", db_path, "--json"])
        stats = json.loads(out)
        self.assertGreater(stats["total_nodes"], 0)


if __name__ == "__main__":
    unittest.main()
