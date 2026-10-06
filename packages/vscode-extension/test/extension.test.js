import test from "node:test";
import assert from "node:assert/strict";
import { resolve } from "node:path";
import { existsSync, readFileSync } from "node:fs";

test("VSCode Extension Manifest & Structure Verification", () => {
  const root = resolve(import.meta.dirname, "..");
  const pkgPath = resolve(root, "package.json");
  assert.ok(existsSync(pkgPath), "package.json must exist");

  const pkg = JSON.parse(readFileSync(pkgPath, "utf-8"));
  assert.equal(pkg.name, "agentgraph-vscode");
  assert.equal(pkg.publisher, "BaylyAI");
  assert.equal(pkg.engines?.vscode, "^1.80.0");
  assert.ok(pkg.contributes?.commands?.length >= 5, "Must declare core commands");
  assert.ok(pkg.contributes?.views?.["agentgraph-explorer"]?.length >= 5, "Must contribute 5 plane views");

  // Check SVG and PNG media assets
  assert.ok(existsSync(resolve(root, "media/agentgraph.svg")), "agentgraph.svg must exist");
  assert.ok(existsSync(resolve(root, "media/agentgraph.png")), "agentgraph.png must exist");
});

test("VSCode Extension Client CLI Bridge Test", async () => {
  const { ExtensionAgentGraphClient } = await import("../src/client.ts");
  const workspaceDir = resolve(import.meta.dirname, "../../..");
  const client = new ExtensionAgentGraphClient({ workspaceDir });

  assert.ok(client, "Client instance created");
  
  // Verify stats query
  const stats = await client.getStats();
  assert.ok(stats.total_nodes > 0, "Graph must have indexed nodes");
  assert.ok(stats.total_edges > 0, "Graph must have indexed edges");

  // Verify DAG validation
  const validation = await client.validate();
  assert.equal(typeof validation.is_valid, "boolean");

  // Verify Mermaid Export
  const mermaid = await client.exportDiagram("mermaid");
  assert.ok(mermaid.includes("flowchart") || mermaid.includes("graph"));

  // Verify BM25 search
  const queryRes = await client.query("developer", undefined, 5);
  assert.ok(Array.isArray(queryRes));
});
