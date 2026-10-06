export type AgentGraphPlane = "agents" | "workflows" | "rules" | "knowledge" | "code";

export interface GraphNode {
  id: string;
  plane: AgentGraphPlane;
  label: string;
  filepath?: string;
  line_number?: number;
  content_preview?: string;
  metadata?: Record<string, any>;
}

export interface GraphEdge {
  id?: number;
  source_id: string;
  target_id: string;
  relation: string;
  plane_cross: number;
}

export interface SearchResult {
  node_id: string;
  plane: AgentGraphPlane;
  label: string;
  filepath?: string;
  score: number;
  snippet?: string;
}

export interface TraversalHop {
  depth: number;
  node: GraphNode;
  relation: string;
  direction: "outgoing" | "incoming";
}

export interface GraphValidationReport {
  is_valid: boolean;
  total_nodes: number;
  total_edges: number;
  cycles: string[][];
  dangling_edges: Array<{
    source_id: string;
    target_id: string;
    missing: string;
  }>;
  isolated_nodes: string[];
}

export interface GraphStats {
  total_nodes: number;
  total_edges: number;
  cross_plane_edges: number;
  planes: {
    agents: number;
    workflows: number;
    rules: number;
    knowledge: number;
    code: number;
  };
}
