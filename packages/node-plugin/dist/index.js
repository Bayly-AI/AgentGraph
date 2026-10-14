import { AgentGraphClient } from "./client.js";

export * from "./types.js";
export { AgentGraphClient, AgentGraphClient as AgentGraph } from "./client.js";

/**
 * Main AgentGraph Node.js Plugin class.
 */
export class AgentGraphPlugin {
  constructor(options = {}) {
    this.client = new AgentGraphClient(options);
  }

  /**
   * Express / Connect middleware for attaching AgentGraph client to requests.
   */
  expressMiddleware() {
    return (req, _res, next) => {
      req.agentGraph = this.client;
      next();
    };
  }
}
