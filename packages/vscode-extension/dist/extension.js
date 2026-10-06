import * as vscode from "vscode";
import { ExtensionAgentGraphClient } from "./client.js";
import { AgentGraphCommands } from "./commands.js";
import {
  AgentGraphPlaneTreeDataProvider,
} from "./treeViews/agentGraphTreeProvider.js";
import { AgentGraphStatsTreeDataProvider } from "./treeViews/statsTreeProvider.js";

let statusBarItem;

export function activate(context) {
  const workspaceFolders = vscode.workspace.workspaceFolders;
  const workspaceDir =
    workspaceFolders && workspaceFolders.length > 0
      ? workspaceFolders[0].uri.fsPath
      : process.cwd();

  const config = vscode.workspace.getConfiguration("agentgraph");
  const cliPath = config.get("cliPath", "");
  const pythonPath = config.get("pythonPath", "python3");
  const dbPath = config.get("dbPath", ".agentgraph/graph.db");

  const client = new ExtensionAgentGraphClient({
    workspaceDir,
    cliPath,
    pythonPath,
    dbPath,
  });

  const statsProvider = new AgentGraphStatsTreeDataProvider(client);
  const agentsProvider = new AgentGraphPlaneTreeDataProvider(client, "agents");
  const workflowsProvider = new AgentGraphPlaneTreeDataProvider(client, "workflows");
  const rulesProvider = new AgentGraphPlaneTreeDataProvider(client, "rules");
  const knowledgeProvider = new AgentGraphPlaneTreeDataProvider(client, "knowledge");
  const codeProvider = new AgentGraphPlaneTreeDataProvider(client, "code");

  const refreshAll = () => {
    statsProvider.refresh();
    agentsProvider.refresh();
    workflowsProvider.refresh();
    rulesProvider.refresh();
    knowledgeProvider.refresh();
    codeProvider.refresh();
    updateStatusBar();
  };

  context.subscriptions.push(
    vscode.window.registerTreeDataProvider("agentgraph.statsView", statsProvider),
    vscode.window.registerTreeDataProvider("agentgraph.agentsView", agentsProvider),
    vscode.window.registerTreeDataProvider("agentgraph.workflowsView", workflowsProvider),
    vscode.window.registerTreeDataProvider("agentgraph.rulesView", rulesProvider),
    vscode.window.registerTreeDataProvider("agentgraph.knowledgeView", knowledgeProvider),
    vscode.window.registerTreeDataProvider("agentgraph.codeView", codeProvider)
  );

  statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 90);
  statusBarItem.command = "agentgraph.exportMermaid";
  statusBarItem.tooltip = "Click to open AgentGraph interactive visual topology";
  context.subscriptions.push(statusBarItem);

  const updateStatusBar = async () => {
    try {
      const stats = await client.getStats();
      statusBarItem.text = `$(symbol-structure) AgentGraph (${stats.total_nodes} nodes)`;
      statusBarItem.show();
    } catch {
      statusBarItem.text = `$(symbol-structure) AgentGraph (Sync needed)`;
      statusBarItem.show();
    }
  };

  updateStatusBar();

  const commands = new AgentGraphCommands(client, refreshAll, context.extensionUri);
  commands.register(context);

  context.subscriptions.push(
    vscode.workspace.onDidSaveTextDocument((doc) => {
      const autoSync = vscode.workspace
        .getConfiguration("agentgraph")
        .get("autoSyncOnSave", true);

      if (!autoSync) return;

      const path = doc.uri.fsPath;
      if (
        path.includes("AGENTS.md") ||
        path.includes(".agentgraph") ||
        path.endsWith(".py") ||
        path.endsWith(".ts") ||
        path.endsWith(".js")
      ) {
        client.sync().then(() => {
          refreshAll();
        }).catch(() => {});
      }
    })
  );
}

export function deactivate() {
  if (statusBarItem) {
    statusBarItem.dispose();
  }
}
