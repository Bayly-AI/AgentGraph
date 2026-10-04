import test from "node:test";
import assert from "node:assert/strict";
import { AgentGraphClient, AgentGraphPlugin } from "../dist/index.js";

test("AgentGraphClient initialises correctly with default options", () => {
  const client = new AgentGraphClient();
  assert.ok(client.workspaceDir.length > 0);
  assert.ok(client.cliPath.length > 0);
  assert.ok(client.dbPath.endsWith("graph.db"));
});

test("AgentGraphPlugin instantiates underlying client", () => {
  const plugin = new AgentGraphPlugin();
  assert.ok(plugin.client instanceof AgentGraphClient);
});

test("AgentGraph Express middleware attaches client to req object", () => {
  const plugin = new AgentGraphPlugin();
  const middleware = plugin.expressMiddleware();
  const req = {};
  const res = {};
  let nextCalled = false;
  middleware(req, res, () => {
    nextCalled = true;
  });
  assert.ok(nextCalled);
  assert.ok(req.agentGraph instanceof AgentGraphClient);
});
