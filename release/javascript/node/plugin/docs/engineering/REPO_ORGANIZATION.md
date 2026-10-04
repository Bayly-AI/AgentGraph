# AgentGraph Repository Organization & Branch Governance

## 1. Directory Structure

```
AgentGraph/
├── .agentgraph/                     # Initialized workspace configuration
│   ├── config.json                  # Workspace settings
│   ├── agents/                      # Role JSON specifications
│   ├── workflows/                   # Workflow DAG JSON definitions
│   ├── rules/                       # Invariant JSON policies
│   ├── knowledge/                   # Markdown architecture docs
│   └── graph.db                     # SQLite graph database
├── .github/
│   ├── CODEOWNERS                   # Assigns @raybayly as sole required reviewer
│   ├── pull_request_template.md     # PR requirements & checklist
│   └── workflows/
│       ├── quality_gates.yml        # CI test & quality gates
│       ├── branch_compliance.yml    # Branch verification & PR checks
│       └── npm-publish.yml          # Release publishing to npm
├── agentgraph/                      # Core Python Engine
│   ├── core/                        # Graph engine, storage, BM25 search, traversal
│   ├── sync/                        # Filesystem crawler, AST parser, Markdown parser
│   ├── init/                        # Initializer and template definitions
│   ├── export/                      # Mermaid, Graphviz DOT, and JSON exporters
│   ├── cli.py                       # Command line interface
│   └── mcp.py                       # Model Context Protocol stdio server
├── docs/                            # Comprehensive documentation
├── packages/
│   └── node-plugin/                 # TypeScript Node.js Plugin SDK
├── release/
│   ├── python/cli/                  # Standalone zipapp executable & wheels
│   └── javascript/node/plugin/      # npm release package & tarballs
└── tests/                           # Unit test suites
```

---

## 2. Branch Governance & PR Protection

- **Open Source:** Anyone can fork and clone the repo.
- **Protected Branches:** Direct push to `development`, `master`, `main`, `staging`, `testing` is locked to repo admins.
- **PR Workflow:** All contributions must target `development` and require review and approval from **Ray Bayly (`@raybayly`)**.
