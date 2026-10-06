import * as vscode from "vscode";

export class AgentGraphPlaneTreeItem extends vscode.TreeItem {
  constructor(
    label,
    plane,
    nodeId,
    filepath,
    lineNumber,
    collapsibleState = vscode.TreeItemCollapsibleState.None,
    detail
  ) {
    super(label, collapsibleState);
    this.label = label;
    this.plane = plane;
    this.nodeId = nodeId;
    this.filepath = filepath;
    this.lineNumber = lineNumber;
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

export class AgentGraphPlaneTreeDataProvider {
  constructor(client, plane) {
    this.client = client;
    this.plane = plane;
    this._onDidChangeTreeData = new vscode.EventEmitter();
    this.onDidChangeTreeData = this._onDidChangeTreeData.event;
  }

  refresh() {
    this._onDidChangeTreeData.fire();
  }

  getTreeItem(element) {
    return element;
  }

  async getChildren(element) {
    if (element) {
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
      const results = await this.client.query("", this.plane, 100);
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
