import { execFile, execFileSync } from "node:child_process";
import { existsSync } from "node:fs";
import { resolve } from "node:path";
import { promisify } from "node:util";
import type {
  AgentGraphPlane,
  GraphStats,
  GraphValidationReport,
  PluginOptions,
  SearchResult,
  TraversalHop,
} from "./types.ts";

const execFileAsync = promisify(execFile);

/**
 * High-performance AgentGraph Client for Node.js environments.
 */
export class AgentGraphClient {
  public workspaceDir: string;
  public cliPath: string;
  public dbPath: string;

  constructor(options: PluginOptions = {}) {
    this.workspaceDir = resolve(options.workspaceDir || process.cwd());

    if (options.cliPath) {
      this.cliPath = resolve(options.cliPath);
    } else {
      let curr = this.workspaceDir;
      let found: string | null = null;
      for (let i = 0; i < 5; i++) {
        const candidate = resolve(curr, "release/python/cli/agentgraph");
        if (existsSync(candidate)) {
          found = candidate;
          break;
        }
        const parent = resolve(curr, "..");
        if (parent === curr) break;
        curr = parent;
      }
      this.cliPath = found || "agentgraph";
    }

    this.dbPath = options.dbPath
      ? resolve(options.dbPath)
      : resolve(this.workspaceDir, ".agentgraph/graph.db");
  }

  /**
   * Run CLI command asynchronously.
   */
  public async runCommand(args: string[]): Promise<string> {
    try {
      const { stdout } = await execFileAsync(this.cliPath, args, {
        cwd: this.workspaceDir,
      });
      return stdout.trim();
    } catch (err: any) {
      const errMsg = err.stderr || err.stdout || err.message;
      throw new Error(`[AgentGraph CLI Error] ${errMsg}`);
    }
  }

  /**
   * Run CLI command synchronously.
   */
  public runCommandSync(args: string[]): string {
    try {
      return execFileSync(this.cliPath, args, {
        cwd: this.workspaceDir,
        encoding: "utf-8",
      }).trim();
    } catch (err: any) {
      const errMsg = err.stderr || err.stdout || err.message;
      throw new Error(`[AgentGraph CLI Error] ${errMsg}`);
    }
  }

  /**
   * Initialize workspace layout (.agentgraph/, AGENTS.md, git hooks).
   */
  public async init(noHooks: boolean = false): Promise<string> {
    const args = ["init", "--dir", this.workspaceDir];
    if (noHooks) args.push("--no-hooks");
    return await this.runCommand(args);
  }

  /**
   * Sync workspace files, rules, workflows, and AST into graph database.
   */
  public async sync(): Promise<string> {
    return await this.runCommand(["sync", "--dir", this.workspaceDir, "--db", this.dbPath]);
  }

  /**
   * Query graph nodes using BM25 lexical ranking.
   */
  public async query(queryText: string, plane?: AgentGraphPlane, limit: number = 10): Promise<SearchResult[]> {
    const args = ["query", queryText, "--db", this.dbPath, "--limit", String(limit), "--json"];
    if (plane) args.push("--plane", plane);
    const output = await this.runCommand(args);
    return JSON.parse(output);
  }

  /**
   * Traverse graph from starting node.
   */
  public async traverse(options: {
    nodeId: string;
    direction?: "outgoing" | "incoming" | "both";
    depth?: number;
    relation?: string;
  }): Promise<TraversalHop[]> {
    const args = ["traverse", options.nodeId, "--db", this.dbPath, "--json"];
    if (options.direction) args.push("--direction", options.direction);
    if (options.depth) args.push("--depth", String(options.depth));
    if (options.relation) args.push("--relation", options.relation);
    const output = await this.runCommand(args);
    return JSON.parse(output);
  }

  /**
   * Topologically resolve dependencies for a given node.
   */
  public async resolveDependencies(nodeId: string): Promise<string[]> {
    const args = ["resolve", nodeId, "--db", this.dbPath, "--json"];
    const output = await this.runCommand(args);
    const parsed = JSON.parse(output);
    return parsed.dependencies || [];
  }

  /**
   * Audit graph topology for cycles, dangling edges, and isolated nodes.
   */
  public async validate(): Promise<GraphValidationReport> {
    const output = await this.runCommand(["validate", "--dir", this.workspaceDir, "--db", this.dbPath, "--json"]);
    return JSON.parse(output);
  }

  /**
   * Export graph topology as Mermaid diagram, Graphviz DOT, or JSON.
   */
  public async export(format: "mermaid" | "dot" | "json" = "mermaid", plane?: AgentGraphPlane): Promise<string> {
    const args = ["export", "--format", format, "--db", this.dbPath];
    if (plane) args.push("--plane", plane);
    return await this.runCommand(args);
  }

  /**
   * Get graph statistical metrics.
   */
  public async getStats(): Promise<GraphStats> {
    const output = await this.runCommand(["stats", "--db", this.dbPath, "--json"]);
    return JSON.parse(output);
  }

  /**
   * Run full Quality Gates validation suite.
   */
  public async runQualityGate(): Promise<{ success: boolean; output: string }> {
    try {
      const output = await this.runCommand(["quality-gate", "--dir", this.workspaceDir, "--db", this.dbPath]);
      return { success: true, output };
    } catch (err: any) {
      return { success: false, output: err.message };
    }
  }
}
