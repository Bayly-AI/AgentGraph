import { existsSync } from "node:fs";
import { resolve } from "node:path";
import * as vscode from "vscode";
import type { ExtensionAgentGraphClient } from "./client.js";
import { AgentGraphWebviewPanel } from "./graphWebview.js";
import type { AgentGraphPlane, SearchResult } from "./types.js";

export class AgentGraphCommands {
  private outputChannel: vscode.OutputChannel;

  constructor(
    private client: ExtensionAgentGraphClient,
    private refreshCallback: () => void,
    private extensionUri: vscode.Uri
  ) {
    this.outputChannel = vscode.window.createOutputChannel("AgentGraph");
  }

  public register(context: vscode.ExtensionContext) {
    context.subscriptions.push(
      this.outputChannel,
      vscode.commands.registerCommand("agentgraph.sync", () => this.handleSync()),
      vscode.commands.registerCommand("agentgraph.query", () => this.handleQuery()),
      vscode.commands.registerCommand("agentgraph.validate", () => this.handleValidate()),
      vscode.commands.registerCommand("agentgraph.resolve", (nodeId?: string) =>
        this.handleResolve(nodeId)
      ),
      vscode.commands.registerCommand(
        "agentgraph.exportMermaid",
        (plane?: AgentGraphPlane) => this.handleExportMermaid(plane)
      ),
      vscode.commands.registerCommand("agentgraph.qualityGate", () =>
        this.handleQualityGate()
      ),
      vscode.commands.registerCommand("agentgraph.refresh", () => this.handleRefresh()),
      vscode.commands.registerCommand(
        "agentgraph.openNode",
        (filepath?: string, line?: number) => this.handleOpenNode(filepath, line)
      )
    );
  }

  public async handleSync(): Promise<void> {
    try {
      vscode.window.withProgress(
        {
          location: vscode.ProgressLocation.Notification,
          title: "AgentGraph: Synchronizing Workspace Substrate...",
          cancellable: false,
        },
        async () => {
          const result = await this.client.sync();
          this.outputChannel.appendLine(`[AgentGraph Sync] ${result}`);
          vscode.window.showInformationMessage("AgentGraph substrate synchronized successfully.");
          this.refreshCallback();
        }
      );
    } catch (err: any) {
      vscode.window.showErrorMessage(`AgentGraph Sync Failed: ${err.message}`);
    }
  }

  public async handleQuery(): Promise<void> {
    const queryText = await vscode.window.showInputBox({
      prompt: "Enter BM25 search query across AgentGraph planes",
      placeHolder: "e.g., developer, feature_delivery, GRAPH-INV-001",
    });

    if (!queryText || queryText.trim().length === 0) return;

    try {
      const results: SearchResult[] = await this.client.query(queryText, undefined, 30);

      if (results.length === 0) {
        vscode.window.showInformationMessage(`No nodes found matching "${queryText}".`);
        return;
      }

      const quickPickItems = results.map((r) => ({
        label: `$(symbol-structure) ${r.label}`,
        description: `[${r.plane.toUpperCase()}] score: ${r.score.toFixed(3)}`,
        detail: r.filepath ? `${r.filepath}` : r.snippet || r.node_id,
        node: r,
      }));

      const selected = await vscode.window.showQuickPick(quickPickItems, {
        placeHolder: `Found ${results.length} results for "${queryText}"`,
      });

      if (selected && selected.node.filepath) {
        this.handleOpenNode(selected.node.filepath, 1);
      }
    } catch (err: any) {
      vscode.window.showErrorMessage(`AgentGraph Query Error: ${err.message}`);
    }
  }

  public async handleValidate(): Promise<void> {
    try {
      const report = await this.client.validate();
      if (report.is_valid) {
        vscode.window.showInformationMessage(
          `✓ AgentGraph Topology Valid: ${report.total_nodes} nodes, ${report.total_edges} edges, strictly DAG.`
        );
      } else {
        const cycleMsg = report.cycles.length > 0 ? `${report.cycles.length} cycles detected.` : "";
        const danglingMsg =
          report.dangling_edges.length > 0
            ? `${report.dangling_edges.length} dangling edges detected.`
            : "";
        vscode.window.showErrorMessage(
          `⚠ AgentGraph Topology Invalid: ${cycleMsg} ${danglingMsg}`
        );
      }
      this.refreshCallback();
    } catch (err: any) {
      vscode.window.showErrorMessage(`AgentGraph Validation Error: ${err.message}`);
    }
  }

  public async handleResolve(nodeId?: string): Promise<void> {
    let target = nodeId;
    if (!target) {
      target = await vscode.window.showInputBox({
        prompt: "Enter Node ID to resolve topological dependencies",
        placeHolder: "e.g. workflow:feature_delivery_pipeline or agent:developer",
      });
    }

    if (!target || target.trim().length === 0) return;

    try {
      const deps = await this.client.resolveDependencies(target);
      this.outputChannel.show(true);
      this.outputChannel.appendLine(`==============================================`);
      this.outputChannel.appendLine(`Topological Dependency Resolution for: ${target}`);
      this.outputChannel.appendLine(`==============================================`);
      if (deps.length === 0) {
        this.outputChannel.appendLine("No prerequisite dependencies found. Ready for immediate execution.");
      } else {
        deps.forEach((dep, idx) => {
          this.outputChannel.appendLine(`  ${idx + 1}. ${dep}`);
        });
      }
      vscode.window.showInformationMessage(
        `Resolved ${deps.length} prerequisite dependencies for ${target}. See Output Channel.`
      );
    } catch (err: any) {
      vscode.window.showErrorMessage(`Dependency Resolution Failed: ${err.message}`);
    }
  }

  public handleExportMermaid(plane?: AgentGraphPlane): void {
    AgentGraphWebviewPanel.createOrShow(this.extensionUri, this.client, plane);
  }

  public async handleQualityGate(): Promise<void> {
    this.outputChannel.show(true);
    this.outputChannel.appendLine(`\n[AgentGraph] Starting Quality Gate Suite...`);
    vscode.window.withProgress(
      {
        location: vscode.ProgressLocation.Notification,
        title: "AgentGraph: Running Quality Gates...",
      },
      async () => {
        const res = await this.client.runQualityGate();
        this.outputChannel.appendLine(res.output);
        if (res.success) {
          vscode.window.showInformationMessage("AgentGraph: All Quality Gates Passed cleanly!");
        } else {
          vscode.window.showErrorMessage("AgentGraph: Quality Gate Failed. See Output Channel.");
        }
      }
    );
  }

  public handleRefresh(): void {
    this.refreshCallback();
  }

  public async handleOpenNode(filepath?: string, line: number = 1): Promise<void> {
    if (!filepath) return;

    let targetPath = filepath;
    if (!existsSync(targetPath)) {
      targetPath = resolve(this.client.workspaceDir, filepath);
    }

    if (!existsSync(targetPath)) {
      vscode.window.showWarningMessage(`File not found: ${filepath}`);
      return;
    }

    try {
      const doc = await vscode.workspace.openTextDocument(targetPath);
      const editor = await vscode.window.showTextDocument(doc);
      const pos = new vscode.Position(Math.max(0, line - 1), 0);
      editor.selection = new vscode.Selection(pos, pos);
      editor.revealRange(new vscode.Range(pos, pos), vscode.TextEditorRevealType.InCenter);
    } catch (err: any) {
      vscode.window.showErrorMessage(`Unable to open file: ${err.message}`);
    }
  }
}
