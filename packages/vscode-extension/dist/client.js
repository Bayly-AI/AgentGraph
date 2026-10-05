import { execFile } from "node:child_process";
import { existsSync } from "node:fs";
import { resolve } from "node:path";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);

export class ExtensionAgentGraphClient {
  constructor(config = {}) {
    this.workspaceDir = resolve(config.workspaceDir || process.cwd());
    this.pythonPath = config.pythonPath || "python3";
    this.dbPath = config.dbPath
      ? resolve(this.workspaceDir, config.dbPath)
      : resolve(this.workspaceDir, ".agentgraph/graph.db");

    if (config.cliPath && config.cliPath.trim().length > 0) {
      this.cliPath = resolve(this.workspaceDir, config.cliPath);
    } else {
      let curr = this.workspaceDir;
      let found = null;
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

  async run(args) {
    try {
      const { stdout } = await execFileAsync(this.cliPath, args, {
        cwd: this.workspaceDir,
      });
      return stdout.trim();
    } catch (cliErr) {
      try {
        const pythonArgs = ["-m", "agentgraph", ...args];
        const { stdout } = await execFileAsync(this.pythonPath, pythonArgs, {
          cwd: this.workspaceDir,
        });
        return stdout.trim();
      } catch (pyErr) {
        const detail = pyErr.stderr || pyErr.stdout || pyErr.message || cliErr.message;
        throw new Error(`[AgentGraph Engine Error] ${detail}`);
      }
    }
  }

  async sync() {
    return await this.run(["sync", "--dir", this.workspaceDir, "--db", this.dbPath]);
  }

  async getStats() {
    const output = await this.run(["stats", "--db", this.dbPath, "--json"]);
    return JSON.parse(output);
  }

  async validate() {
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

  async query(queryText, plane, limit = 20) {
    const args = ["query", queryText, "--db", this.dbPath, "--limit", String(limit), "--json"];
    if (plane) args.push("--plane", plane);
    const output = await this.run(args);
    return JSON.parse(output);
  }

  async traverse(nodeId, depth = 2) {
    const args = ["traverse", nodeId, "--depth", String(depth), "--db", this.dbPath, "--json"];
    const output = await this.run(args);
    return JSON.parse(output);
  }

  async resolveDependencies(nodeId) {
    const args = ["resolve", nodeId, "--db", this.dbPath, "--json"];
    const output = await this.run(args);
    const parsed = JSON.parse(output);
    return parsed.dependencies || [];
  }

  async exportDiagram(format = "mermaid", plane) {
    const args = ["export", "--format", format, "--db", this.dbPath];
    if (plane) args.push("--plane", plane);
    return await this.run(args);
  }

  async runQualityGate() {
    try {
      const output = await this.run([
        "quality-gate",
        "--dir",
        this.workspaceDir,
        "--db",
        this.dbPath,
      ]);
      return { success: true, output };
    } catch (err) {
      return { success: false, output: err.message };
    }
  }
}
