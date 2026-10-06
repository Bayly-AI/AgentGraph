import tempfile
import unittest
from pathlib import Path

from agentgraph.sync.code_parser import CodeASTParser


class TestCodeASTParser(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp_dir.name)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_parse_python_file(self):
        py_code = '''
"""Sample module docstring."""

class BaseEngine:
    pass

class CustomEngine(BaseEngine):
    def process(self, data):
        """Processes data items."""
        return True

def standalone_helper():
    return 42
'''
        fpath = self.root / "sample.py"
        fpath.write_text(py_code, encoding="utf-8")

        nodes, edges = CodeASTParser.parse_python_file(fpath)
        node_ids = [n.id for n in nodes]

        self.assertIn("ast:mod:sample", node_ids)
        self.assertIn("ast:class:sample:BaseEngine", node_ids)
        self.assertIn("ast:class:sample:CustomEngine", node_ids)
        self.assertIn("ast:func:sample:CustomEngine.process", node_ids)
        self.assertIn("ast:func:sample:standalone_helper", node_ids)

        relations = [e.relation for e in edges]
        self.assertIn("CONTAINS_CLASS", relations)
        self.assertIn("CONTAINS_FUNCTION", relations)
        self.assertIn("INHERITS_FROM", relations)

    def test_parse_js_ts_file(self):
        ts_code = '''
export class GraphClient extends BaseClient {
    public async query() {
        return [];
    }
}

export function initClient() {
    return new GraphClient();
}
'''
        fpath = self.root / "client.ts"
        fpath.write_text(ts_code, encoding="utf-8")

        nodes, edges = CodeASTParser.parse_js_ts_file(fpath)
        node_ids = [n.id for n in nodes]

        self.assertIn("ast:mod:client", node_ids)
        self.assertIn("ast:class:client:GraphClient", node_ids)
        self.assertIn("ast:func:client:initClient", node_ids)


if __name__ == "__main__":
    unittest.main()
