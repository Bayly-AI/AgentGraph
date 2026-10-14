import type {
  AgentGraphPlane,
  GraphStats,
  GraphValidationReport,
  PluginOptions,
  SearchResult,
  TraversalHop,
} from "./types.js";

export declare class AgentGraphClient {
  workspaceDir: string;
  cliPath: string;
  dbPath: string;

  constructor(options?: PluginOptions);

  runCommand(args: string[]): Promise<string>;
  runCommandSync(args: string[]): string;

  init(noHooks?: boolean): Promise<string>;
  sync(): Promise<string>;
  query(queryText: string, plane?: AgentGraphPlane, limit?: number): Promise<SearchResult[]>;
  traverse(options: {
    nodeId: string;
    direction?: "outgoing" | "incoming" | "both";
    depth?: number;
    relation?: string;
  }): Promise<TraversalHop[]>;
  resolveDependencies(nodeId: string): Promise<string[]>;
  validate(): Promise<GraphValidationReport>;
  export(format?: "mermaid" | "dot" | "json", plane?: AgentGraphPlane): Promise<string>;
  getStats(): Promise<GraphStats>;
  runQualityGate(): Promise<{ success: boolean; output: string }>;
}
