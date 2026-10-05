import { execFile } from "node:child_process";
import { existsSync } from "node:fs";
import { resolve } from "node:path";
import { promisify } from "node:util";
import type {
  AgentGraphPlane,
  GraphNode,
  GraphStats,
  GraphValidationReport,
  SearchResult,
  TraversalHop,
} from "./types.js";

const execFileAsync = promisify(execFile);

export interface ExtensionClientConfig {
  workspaceDir: string;
  cliPath?: string;
  pythonPath?: string;
  dbPath?: string;
}

export class ExtensionAgentGraphClient {
  public workspaceDir: string;
  public cliPath: string;
  public pythonPath: string;
  public dbPath: string;

  constructor(config: ExtensionClientConfig) {
    this.workspaceDir = resolve(config.workspaceDir || process.cwd());
    this.pythonPath = config.pythonPath || "python3";
    this.dbPath = config.dbPath
      ? resolve(this.workspaceDir, config.dbPath)
      : resolve(this.workspaceDir, ".agentgraph/graph.db");

    if (config.cliPath && config.cliPath.trim().length > 0) {
      this.cliPath = resolve(this.workspaceDir, config.cliPath);
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
  }

  /**
   * Run command via CLI binary or python -m agentgraph fallback.
   */
  public async run(args: string[]): Promise<string> {
    try {
      // Try direct binary first
      const { stdout } = await execFileAsync(this.cliPath, args, {
        cwd: this.workspaceDir,
      });
      return stdout.trim();
    } catch (cliErr: any) {
      // Fallback to python3 -m agentgraph
      try {
        const pythonArgs = ["-m", "agentgraph", ...args];
        const { stdout } = await execFileAsync(this.pythonPath, pythonArgs, {
          cwd: this.workspaceDir,
        });
        return stdout.trim();
      } catch (pyErr: any) {
        const detail = pyErr.stderr || pyErr.stdout || pyErr.message || cliErr.message;
        throw new Error(`[AgentGraph Engine Error] ${detail}`);
      }
    }
  }

  public async sync(): Promise<string> {
    return await this.run(["sync", "--dir", this.workspaceDir, "--db", this.dbPath]);
  }

  public async getStats(): Promise<GraphStats> {
    const output = await this.run(["stats", "--db", this.dbPath, "--json"]);
    return JSON.parse(output);
  }

  public async validate(): Promise<GraphValidationReport> {
    const output = await this.run([
      "validate",
      "--dir",
      this.workspaceDir,
      "--db",
      this.dbPath,
      "--json",
    ]);
    return JSON.parse(output);
  }

  public async query(
    queryText: string,
    plane?: AgentGraphPlane,
    limit: number = 20
  ): Promise<SearchResult[]> {
    const args = ["query", queryText, "--db", this.dbPath, "--limit", String(limit), "--json"];
    if (plane) args.push("--plane", plane);
    const output = await this.run(args);
    return JSON.parse(output);
  }

  public async traverse(nodeId: string, depth: number = 2): Promise<TraversalHop[]> {
    const args = ["traverse", nodeId, "--depth", String(depth), "--db", this.dbPath, "--json"];
    const output = await this.run(args);
    return JSON.parse(output);
  }

  public async resolveDependencies(nodeId: string): Promise<string[]> {
    const args = ["resolve", nodeId, "--db", this.dbPath, "--json"];
    const output = await this.run(args);
    const parsed = JSON.parse(output);
    return parsed.dependencies || [];
  }

  public async exportDiagram(
    format: "mermaid" | "dot" | "json" = "mermaid",
    plane?: AgentGraphPlane
  ): Promise<string> {
    const args = ["export", "--format", format, "--db", this.dbPath];
    if (plane) args.push("--plane", plane);
    return await this.run(args);
  }

  public async runQualityGate(): Promise<{ success: boolean; output: string }> {
    try {
      const output = await this.run([
        "quality-gate",
        "--dir",
        this.workspaceDir,
        "--db",
        this.dbPath,
      ]);
      return { success: true, output };
    } catch (err: any) {
      return { success: false, output: err.message };
    }
  }
}
