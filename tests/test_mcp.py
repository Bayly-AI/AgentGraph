import json
import tempfile
import unittest
from pathlib import Path

from agentgraph.init.initializer import RepositoryInitializer
from agentgraph.mcp import AgentGraphMCPServer
from agentgraph.sync.syncer import RepositorySyncer


class TestMCPServer(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp_dir.name)
        RepositoryInitializer.initialize_repository(target_dir=self.root, install_hooks=False)
        RepositorySyncer.sync_repository(root_dir=self.root, db_path=self.root / ".agentgraph" / "graph.db")
        self.server = AgentGraphMCPServer(workspace_dir=str(self.root))

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_tools_list(self):
        tools = self.server.get_tools_list()
        tool_names = [t["name"] for t in tools]
        self.assertIn("agentgraph_query", tool_names)
        self.assertIn("agentgraph_traverse", tool_names)
        self.assertIn("agentgraph_resolve", tool_names)
        self.assertIn("agentgraph_validate", tool_names)
        self.assertIn("agentgraph_export", tool_names)
        self.assertIn("agentgraph_sync", tool_names)

    def test_query_tool_call(self):
        res = self.server.handle_tool_call("agentgraph_query", {"query": "developer"})
        parsed = json.loads(res)
        self.assertIsInstance(parsed, list)

    def test_validate_tool_call(self):
        res = self.server.handle_tool_call("agentgraph_validate", {})
        parsed = json.loads(res)
        self.assertIn("is_valid", parsed)

    def test_export_tool_call(self):
        res = self.server.handle_tool_call("agentgraph_export", {"format": "mermaid"})
        self.assertIn("flowchart", res)


if __name__ == "__main__":
    unittest.main()
