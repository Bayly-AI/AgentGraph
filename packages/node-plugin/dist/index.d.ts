import { AgentGraphClient } from "./client.js";
import type { PluginOptions } from "./types.js";

export * from "./types.js";
export { AgentGraphClient, AgentGraphClient as AgentGraph } from "./client.js";

export declare class AgentGraphPlugin {
  client: AgentGraphClient;
  constructor(options?: PluginOptions);
  expressMiddleware(): (req: any, _res: any, next: any) => void;
}
