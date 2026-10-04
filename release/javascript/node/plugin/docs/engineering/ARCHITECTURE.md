# AgentGraph Architecture & Substrate Design

## 1. Multi-Plane Architecture

AgentGraph organizes multi-agent cognition into 5 distinct, interconnected planes:

1. **Agents Plane (`agents`):** Agent identities, role specifications, tool permissions, and parent-child inheritance.
2. **Workflows Plane (`workflows`):** Multi-agent execution pipelines, step dependencies (`DEPENDS_ON`), and agent assignments (`ASSIGNED_TO`).
3. **Knowledge Plane (`knowledge`):** Markdown architecture documentation, specifications, and relative links (`REFERENCES`).
4. **Code AST Plane (`code`):** Python and JS/TS AST entities including modules, classes, methods, functions, and inheritance links (`INHERITS_FROM`, `CONTAINS_CLASS`, `CONTAINS_FUNCTION`).
5. **Rules Plane (`rules`):** Invariant policies, standards, and role-governing directives (`GOVERNS`).

---

## 2. Storage & Indexing Subsystem

AgentGraph utilizes a single-file atomic SQLite3 database at `.agentgraph/graph.db`:
- Zero external ORM or C extensions required.
- Standard schema: `nodes`, `edges`.
- Performance indices on `nodes.plane`, `nodes.type`, `edges.source`, `edges.target`, `edges.relation`, and `edges.plane`.

---

## 3. Okapi BM25 Lexical Ranking

BM25 equation implemented:
$$\text{Score}(D, Q) = \sum_{i=1}^{n} \text{IDF}(q_i) \cdot \frac{f(q_i, D) \cdot (k_1 + 1)}{f(q_i, D) + k_1 \cdot \left(1 - b + b \cdot \frac{|D|}{\text{avgdl}}\right)}$$

Where:
- $k_1 = 1.5$
- $b = 0.75$
- $\text{IDF}(q_i) = \ln\left(\frac{N - n(q_i) + 0.5}{n(q_i) + 0.5} + 1\right)$
