import { AgentGraphClient } from "./client.ts";
import type { PluginOptions } from "./types.ts";

export type * from "./types.ts";
export { AgentGraphClient, AgentGraphClient as AgentGraph } from "./client.ts";

/**
 * Main AgentGraph Node.js Plugin class.
 */
export class AgentGraphPlugin {
  public client: AgentGraphClient;

  constructor(options: PluginOptions = {}) {
    this.client = new AgentGraphClient(options);
  }

  /**
   * Express / Connect middleware for attaching AgentGraph client to requests.
   */
  public expressMiddleware() {
    return (req: any, _res: any, next: any) => {
      req.agentGraph = this.client;
      next();
    };
  }
}
