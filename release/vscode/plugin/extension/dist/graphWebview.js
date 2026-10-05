import * as vscode from "vscode";

export class AgentGraphWebviewPanel {
  static currentPanel = undefined;
  static viewType = "agentgraph.mermaidViewer";

  static createOrShow(extensionUri, client, plane) {
    const column = vscode.window.activeTextEditor
      ? vscode.window.activeTextEditor.viewColumn
      : undefined;

    if (AgentGraphWebviewPanel.currentPanel) {
      AgentGraphWebviewPanel.currentPanel._panel.reveal(column);
      if (plane !== undefined) {
        AgentGraphWebviewPanel.currentPanel.setPlane(plane);
      }
      AgentGraphWebviewPanel.currentPanel.update();
      return;
    }

    const panel = vscode.window.createWebviewPanel(
      AgentGraphWebviewPanel.viewType,
      "AgentGraph Multi-Plane Topology",
      column || vscode.ViewColumn.One,
      {
        enableScripts: true,
        retainContextWhenHidden: true,
      }
    );

    AgentGraphWebviewPanel.currentPanel = new AgentGraphWebviewPanel(
      panel,
      extensionUri,
      client,
      plane
    );
  }

  constructor(panel, extensionUri, client, plane) {
    this._panel = panel;
    this._extensionUri = extensionUri;
    this.client = client;
    this._selectedPlane = plane;
    this._disposables = [];

    this.update();

    this._panel.onDidDispose(() => this.dispose(), null, this._disposables);

    this._panel.webview.onDidReceiveMessage(
      async (message) => {
        switch (message.command) {
          case "refresh":
            await this.update();
            break;
          case "changePlane":
            this._selectedPlane = message.plane ? message.plane : undefined;
            await this.update();
            break;
          case "nodeClicked":
            if (message.nodeId) {
              vscode.commands.executeCommand("agentgraph.resolve", message.nodeId);
            }
            break;
        }
      },
      null,
      this._disposables
    );
  }

  setPlane(plane) {
    this._selectedPlane = plane;
  }

  async update() {
    this._panel.title = `AgentGraph: ${
      this._selectedPlane ? this._selectedPlane.toUpperCase() : "Full Topology"
    }`;
    this._panel.webview.html = await this._getHtmlForWebview();
  }

  dispose() {
    AgentGraphWebviewPanel.currentPanel = undefined;
    this._panel.dispose();
    while (this._disposables.length) {
      const x = this._disposables.pop();
      if (x) {
        x.dispose();
      }
    }
  }

  async _getHtmlForWebview() {
    let mermaidCode = "";
    try {
      mermaidCode = await this.client.exportDiagram("mermaid", this._selectedPlane);
    } catch (err) {
      mermaidCode = `flowchart TD\n  Error["Error loading graph: ${err.message}"]`;
    }

    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AgentGraph Topology</title>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
  <style>
    :root {
      --bg: var(--vscode-editor-background, #0d1117);
      --fg: var(--vscode-editor-foreground, #c9d1d9);
      --border: var(--vscode-widget-border, #30363d);
      --accent: var(--vscode-button-background, #238636);
    }
    body {
      background-color: var(--bg);
      color: var(--fg);
      font-family: var(--vscode-font-family, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif);
      margin: 0;
      padding: 0;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      height: 100vh;
    }
    .header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 10px 16px;
      border-bottom: 1px solid var(--border);
      background: var(--vscode-editor-background);
      z-index: 10;
    }
    .title {
      font-weight: 600;
      font-size: 14px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .controls {
      display: flex;
      gap: 8px;
      align-items: center;
    }
    select, button {
      background: var(--vscode-dropdown-background, #21262d);
      color: var(--vscode-dropdown-foreground, #c9d1d9);
      border: 1px solid var(--border);
      padding: 5px 10px;
      border-radius: 4px;
      font-size: 12px;
      cursor: pointer;
    }
    button:hover, select:hover {
      background: var(--vscode-button-hoverBackground, #30363d);
    }
    .graph-container {
      flex: 1;
      overflow: auto;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 24px;
      cursor: grab;
    }
    .graph-container:active {
      cursor: grabbing;
    }
    .mermaid {
      max-width: 100%;
    }
    .mermaid svg {
      height: auto;
      max-height: 85vh;
    }
  </style>
</head>
<body>
  <div class="header">
    <div class="title">
      <span>⚡ AgentGraph Multi-Plane Topology</span>
    </div>
    <div class="controls">
      <select id="planeSelect" onchange="onPlaneChange(this.value)">
        <option value="" ${!this._selectedPlane ? "selected" : ""}>All 5 Planes</option>
        <option value="agents" ${this._selectedPlane === "agents" ? "selected" : ""}>Agents Plane</option>
        <option value="workflows" ${this._selectedPlane === "workflows" ? "selected" : ""}>Workflows Plane</option>
        <option value="rules" ${this._selectedPlane === "rules" ? "selected" : ""}>Rules Plane</option>
        <option value="knowledge" ${this._selectedPlane === "knowledge" ? "selected" : ""}>Knowledge Plane</option>
        <option value="code" ${this._selectedPlane === "code" ? "selected" : ""}>Code AST Plane</option>
      </select>
      <button onclick="refresh()">🔄 Refresh</button>
      <button onclick="zoomIn()">➕ Zoom In</button>
      <button onclick="zoomOut()">➖ Zoom Out</button>
      <button onclick="resetZoom()">↺ Reset</button>
    </div>
  </div>

  <div class="graph-container" id="graphContainer">
    <pre class="mermaid" id="mermaidGraph">
${mermaidCode}
    </pre>
  </div>

  <script>
    const vscode = acquireVsCodeApi();
    mermaid.initialize({
      startOnLoad: true,
      theme: 'dark',
      securityLevel: 'loose'
    });

    let currentZoom = 1.0;
    function zoomIn() {
      currentZoom += 0.15;
      applyZoom();
    }
    function zoomOut() {
      if (currentZoom > 0.3) {
        currentZoom -= 0.15;
        applyZoom();
      }
    }
    function resetZoom() {
      currentZoom = 1.0;
      applyZoom();
    }
    function applyZoom() {
      const el = document.getElementById('mermaidGraph');
      if (el) {
        el.style.transform = 'scale(' + currentZoom + ')';
        el.style.transformOrigin = 'center center';
      }
    }

    function onPlaneChange(plane) {
      vscode.postMessage({ command: 'changePlane', plane: plane });
    }

    function refresh() {
      vscode.postMessage({ command: 'refresh' });
    }
  </script>
</body>
</html>`;
  }
}
