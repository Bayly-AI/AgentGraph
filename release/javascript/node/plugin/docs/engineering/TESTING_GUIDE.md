# AgentGraph Testing & Quality Gates Guide

## 1. Running the Test Suites

### Python Unit Tests
```bash
python3 -m unittest discover tests
```

### Node.js Plugin Unit Tests
```bash
node --experimental-strip-types --test packages/node-plugin/test/*.test.ts
```

### Full Quality Gate Execution
```bash
python3 -m agentgraph quality-gate
```

---

## 2. Quality Gate Stages

1. **Gate 1: Workspace Ingestion & Sync:** Parses `AGENTS.md`, rules, agents, workflows, knowledge markdown, and code AST.
2. **Gate 2: Graph Health & Cycle Verification:** Verifies 0 circular dependencies and 0 dangling edges in DAG workflows.
3. **Gate 3: Unit Test Suite:** Executes full Python test suite with 100% pass requirement.
4. **Gate 4: Release Package Verification:** Builds standalone CLI zipapp and npm package tarball.
