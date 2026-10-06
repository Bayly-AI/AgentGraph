import test from "node:test";
import assert from "node:assert";
import { AgentGraphClient, AgentGraphPlugin } from "../src/index.ts";

test("AgentGraphClient initialises correctly with default options", () => {
  const client = new AgentGraphClient();
  assert.ok(client.workspaceDir);
  assert.ok(client.dbPath);
  assert.ok(client.cliPath);
});

test("AgentGraphPlugin instantiates underlying client", () => {
  const plugin = new AgentGraphPlugin();
  assert.ok(plugin.client instanceof AgentGraphClient);
});

test("AgentGraph Express middleware attaches client to req object", () => {
  const plugin = new AgentGraphPlugin();
  const middleware = plugin.expressMiddleware();
  const req: any = {};
  const res: any = {};
  let nextCalled = false;

  middleware(req, res, () => {
    nextCalled = true;
  });

  assert.strictEqual(nextCalled, true);
  assert.strictEqual(req.agentGraph, plugin.client);
});
