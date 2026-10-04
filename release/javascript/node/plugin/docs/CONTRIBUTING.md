# Contributing to AgentGraph

Thank you for your interest in contributing to **AgentGraph**!

AgentGraph is an open source project licensed under the GNU General Public License v3.0 (GPLv3). We welcome contributions from the community.

---

## 🔒 Branch Structure & Access Rules

To ensure stability, architectural integrity, and deterministic quality across all releases:

1. **Public Forking & Cloning:** Anyone may clone or fork the repository.
2. **Protected Branches:** Direct push access to `development`, `master`, `main`, `staging`, and `testing` is strictly restricted to repository administrators (**Ray Bayly** and explicitly authorized admins).
3. **Target Branch for PRs:** All proposed code changes, bug fixes, features, and documentation enhancements must be submitted via Pull Requests targeting the **`development`** branch.
4. **Mandatory Approval:** Every Pull Request requires automated Quality Gate clearance and explicit review/approval by **Ray Bayly (`@raybayly`)** or an appointed administrator before merging.

---

## 🛠️ Development Workflow

### 1. Clone & Set Up

```bash
git clone https://github.com/Bayly-AI/AgentGraph.git
cd AgentGraph
git checkout development
git checkout -b feat/your-feature-name
```

### 2. Local Testing & Quality Gates

Before opening a PR, ensure all tests and quality gates pass:

```bash
# Run unit tests
python3 -m unittest discover tests

# Run full Quality Gates suite
python3 -m agentgraph quality-gate

# Run Node.js plugin tests
node --experimental-strip-types --test packages/node-plugin/test/*.test.ts
```

### 3. Open a Pull Request

- Target: `development`
- Fill out the PR template with a clear description of changes.
- Tag `@raybayly` for review and approval.

---

## 📜 Code Standards

- Maintain zero external core dependencies for the Python engine.
- Write unit tests for all new functions, parsers, and traversal logic.
- Ensure all graph definitions are acyclic and pass `agentgraph validate`.
