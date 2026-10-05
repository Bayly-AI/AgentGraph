import * as vscode from "vscode";
import type { ExtensionAgentGraphClient } from "../client.js";

export class StatsTreeItem extends vscode.TreeItem {
  constructor(
    public readonly label: string,
    public readonly value: string,
    icon: string,
    collapsibleState: vscode.TreeItemCollapsibleState = vscode.TreeItemCollapsibleState.None
  ) {
    super(label, collapsibleState);
    this.description = value;
    this.tooltip = `${label}: ${value}`;
    this.iconPath = new vscode.ThemeIcon(icon);
  }
}

export class AgentGraphStatsTreeDataProvider
  implements vscode.TreeDataProvider<StatsTreeItem>
{
  private _onDidChangeTreeData: vscode.EventEmitter<
    StatsTreeItem | undefined | null | void
  > = new vscode.EventEmitter<StatsTreeItem | undefined | null | void>();
  readonly onDidChangeTreeData: vscode.Event<
    StatsTreeItem | undefined | null | void
  > = this._onDidChangeTreeData.event;

  constructor(private client: ExtensionAgentGraphClient) {}

  public refresh(): void {
    this._onDidChangeTreeData.fire();
  }

  public getTreeItem(element: StatsTreeItem): vscode.TreeItem {
    return element;
  }

  public async getChildren(element?: StatsTreeItem): Promise<StatsTreeItem[]> {
    if (element) return [];

    try {
      const [stats, validation] = await Promise.all([
        this.client.getStats(),
        this.client.validate(),
      ]);

      const items: StatsTreeItem[] = [];

      // Overall Health
      if (validation.is_valid) {
        items.push(
          new StatsTreeItem("DAG Topology", "Valid (Acyclic)", "pass-filled")
        );
      } else {
        const cycleCount = validation.cycles ? validation.cycles.length : 0;
        const danglingCount = validation.dangling_edges ? validation.dangling_edges.length : 0;
        items.push(
          new StatsTreeItem(
            "DAG Topology",
            `INVALID (${cycleCount} cycles, ${danglingCount} dangling)`,
            "error"
          )
        );
      }

      items.push(
        new StatsTreeItem("Total Nodes", String(stats.total_nodes), "symbol-structure")
      );
      items.push(
        new StatsTreeItem("Total Edges", String(stats.total_edges), "git-branch")
      );
      items.push(
        new StatsTreeItem("Cross-Plane Edges", String(stats.cross_plane_edges), "zap")
      );

      // Breakdown per plane
      if (stats.planes) {
        items.push(new StatsTreeItem("Agents Plane Nodes", String(stats.planes.agents || 0), "person"));
        items.push(new StatsTreeItem("Workflows Plane Nodes", String(stats.planes.workflows || 0), "git-merge"));
        items.push(new StatsTreeItem("Rules Plane Nodes", String(stats.planes.rules || 0), "shield"));
        items.push(new StatsTreeItem("Knowledge Plane Nodes", String(stats.planes.knowledge || 0), "book"));
        items.push(new StatsTreeItem("Code AST Nodes", String(stats.planes.code || 0), "symbol-class"));
      }

      return items;
    } catch (err: any) {
      return [
        new StatsTreeItem(
          "Graph Status",
          "Not initialized / Sync needed",
          "warning"
        ),
      ];
    }
  }
}
