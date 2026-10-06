/**
 * Type definitions for AgentGraph Node.js Client & Plugin.
 */

export type AgentGraphPlane = "rules" | "agents" | "workflows" | "knowledge" | "code";

export interface AgentGraphNode {
  id: string;
  plane: string;
  type: string;
  label: string;
  content: string;
  properties: Record<string, any>;
  valid_from?: string | null;
  valid_to?: string | null;
  is_current: boolean;
  created_at: string;
  updated_at: string;
}

export interface AgentGraphEdge {
  source: string;
  target: string;
  relation: string;
  plane: string;
  weight: number;
  valid_from?: string | null;
  valid_to?: string | null;
  is_current: boolean;
  metadata: Record<string, any>;
}

export interface SearchResult {
  node: AgentGraphNode;
  score: number;
  matched_plane: string;
}

export interface TraversalHop {
  node_id: string;
  depth: number;
  edge: AgentGraphEdge | null;
}

export interface GraphValidationReport {
  is_valid: boolean;
  total_nodes: number;
  total_edges: number;
  plane_counts: Record<string, number>;
  dangling_edges: [string, string][];
  detected_cycles: string[][];
  isolated_nodes: string[];
}

export interface GraphStats {
  total_nodes: number;
  total_edges: number;
  plane_node_distribution: Record<string, number>;
  plane_edge_distribution: Record<string, number>;
  relation_distribution: Record<string, number>;
  node_type_distribution: Record<string, number>;
}

export interface PluginOptions {
  cliPath?: string;
  workspaceDir?: string;
  dbPath?: string;
}
