import * as vscode from "vscode";
import type { ExtensionAgentGraphClient } from "../client.js";
import type { AgentGraphPlane, SearchResult } from "../types.js";

export class AgentGraphPlaneTreeItem extends vscode.TreeItem {
  constructor(
    public readonly label: string,
    public readonly plane: AgentGraphPlane,
    public readonly nodeId: string,
    public readonly filepath?: string,
    public readonly lineNumber?: number,
    public readonly collapsibleState: vscode.TreeItemCollapsibleState = vscode.TreeItemCollapsibleState.None,
    public readonly detail?: string
  ) {
    super(label, collapsibleState);
    this.tooltip = `${this.label} (${this.nodeId})`;
    this.description = detail || this.nodeId;
    this.contextValue = "graphNode";

    if (filepath) {
      this.command = {
        command: "agentgraph.openNode",
        title: "Open Node Target",
        arguments: [filepath, lineNumber],
      };
    }

    // Set appropriate theme icons based on plane
    switch (plane) {
      case "agents":
        this.iconPath = new vscode.ThemeIcon("person");
        break;
      case "workflows":
        this.iconPath = new vscode.ThemeIcon("git-merge");
        break;
      case "rules":
        this.iconPath = new vscode.ThemeIcon("shield");
        break;
      case "knowledge":
        this.iconPath = new vscode.ThemeIcon("book");
        break;
      case "code":
        this.iconPath = new vscode.ThemeIcon("symbol-class");
        break;
      default:
        this.iconPath = new vscode.ThemeIcon("symbol-structure");
    }
  }
}

export class AgentGraphPlaneTreeDataProvider
  implements vscode.TreeDataProvider<AgentGraphPlaneTreeItem>
{
  private _onDidChangeTreeData: vscode.EventEmitter<
    AgentGraphPlaneTreeItem | undefined | null | void
  > = new vscode.EventEmitter<AgentGraphPlaneTreeItem | undefined | null | void>();
  readonly onDidChangeTreeData: vscode.Event<
    AgentGraphPlaneTreeItem | undefined | null | void
  > = this._onDidChangeTreeData.event;

  constructor(
    private client: ExtensionAgentGraphClient,
    private plane: AgentGraphPlane
  ) {}

  public refresh(): void {
    this._onDidChangeTreeData.fire();
  }

  public getTreeItem(element: AgentGraphPlaneTreeItem): vscode.TreeItem {
    return element;
  }

  public async getChildren(
    element?: AgentGraphPlaneTreeItem
  ): Promise<AgentGraphPlaneTreeItem[]> {
    if (element) {
      // Child elements could show traversals / outgoing relations
      try {
        const hops = await this.client.traverse(element.nodeId, 1);
        return hops.map((h) => {
          return new AgentGraphPlaneTreeItem(
            `${h.relation} ➔ ${h.node.label}`,
            h.node.plane,
            h.node.id,
            h.node.filepath,
            h.node.line_number,
            vscode.TreeItemCollapsibleState.None,
            h.node.plane
          );
        });
      } catch {
        return [];
      }
    }

    try {
      const results: SearchResult[] = await this.client.query("", this.plane, 100);
      return results.map((r) => {
        return new AgentGraphPlaneTreeItem(
          r.label,
          r.plane,
          r.node_id,
          r.filepath,
          1,
          vscode.TreeItemCollapsibleState.Collapsed,
          r.snippet || ""
        );
      });
    } catch {
      return [];
    }
  }
}
