"""Command-line interface (CLI) for AgentGraph cognitive substrate."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from agentgraph.core.graph import AgentGraphEngine
from agentgraph.export.exporter import GraphExporter
from agentgraph.init.initializer import RepositoryInitializer
from agentgraph.mcp import run_mcp_server
from agentgraph.sync.syncer import RepositorySyncer


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="agentgraph",
        description="AgentGraph: Multi-Plane Cognitive Substrate & Knowledge Graph Engine for AI Agents",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # 1. init
    init_p = subparsers.add_parser("init", help="Initialize workspace with .agentgraph/, templates, AGENTS.md, and hooks")
    init_p.add_argument("--dir", default=".", help="Target workspace directory")
    init_p.add_argument("--no-hooks", action="store_true", help="Skip git pre-commit hook installation")

    # 2. sync
    sync_p = subparsers.add_parser("sync", help="Scan workspace files and synchronize into graph database")
    sync_p.add_argument("--dir", default=".", help="Target workspace root")
    sync_p.add_argument("--db", default=".agentgraph/graph.db", help="SQLite database file path")

    # 3. query
    query_p = subparsers.add_parser("query", help="Perform BM25 search across graph nodes")
    query_p.add_argument("query_str", nargs="?", default="", help="Search query keywords")
    query_p.add_argument("--plane", choices=["rules", "agents", "workflows", "knowledge", "code"], help="Filter by plane")
    query_p.add_argument("--limit", type=int, default=10, help="Max results to return")
    query_p.add_argument("--db", default=".agentgraph/graph.db", help="SQLite database path")
    query_p.add_argument("--json", action="store_true", help="Output JSON format")

    # 4. traverse
    trav_p = subparsers.add_parser("traverse", help="Traverse graph starting from a node")
    trav_p.add_argument("node_id", help="Starting node ID (e.g., 'role:developer', 'ast:mod:cli')")
    trav_p.add_argument("--depth", type=int, default=3, help="Max traversal depth")
    trav_p.add_argument("--direction", choices=["outgoing", "incoming", "both"], default="outgoing", help="Traversal direction")
    trav_p.add_argument("--relation", help="Filter by edge relation type")
    trav_p.add_argument("--db", default=".agentgraph/graph.db", help="SQLite database path")
    trav_p.add_argument("--json", action="store_true", help="Output JSON format")

    # 5. resolve
    res_p = subparsers.add_parser("resolve", help="Topologically resolve dependencies for a given node")
    res_p.add_argument("node_id", help="Node ID to resolve dependencies for")
    res_p.add_argument("--db", default=".agentgraph/graph.db", help="SQLite database path")
    res_p.add_argument("--json", action="store_true", help="Output JSON format")

    # 6. validate
    val_p = subparsers.add_parser("validate", help="Audit graph topology for cycles, dangling edges, and isolated nodes")
    val_p.add_argument("--dir", default=".", help="Workspace root")
    val_p.add_argument("--db", default=".agentgraph/graph.db", help="SQLite database path")
    val_p.add_argument("--json", action="store_true", help="Output JSON format")

    # 7. export
    exp_p = subparsers.add_parser("export", help="Export graph topology as Mermaid, DOT, or JSON")
    exp_p.add_argument("--format", choices=["mermaid", "dot", "json"], default="mermaid", help="Export format")
    exp_p.add_argument("--plane", choices=["rules", "agents", "workflows", "knowledge", "code"], help="Filter by plane")
    exp_p.add_argument("--db", default=".agentgraph/graph.db", help="SQLite database path")
    exp_p.add_argument("--out", help="Write export output to file")

    # 8. stats
    stats_p = subparsers.add_parser("stats", help="Show summary statistics across graph planes")
    stats_p.add_argument("--db", default=".agentgraph/graph.db", help="SQLite database path")
    stats_p.add_argument("--json", action="store_true", help="Output JSON format")

    # 9. quality-gate
    qg_p = subparsers.add_parser("quality-gate", help="Execute multi-stage Quality Gates validation suite")
    qg_p.add_argument("--dir", default=".", help="Workspace root")
    qg_p.add_argument("--db", default=".agentgraph/graph.db", help="SQLite database path")
    qg_p.add_argument("--json", action="store_true", help="Output JSON format")

    # 10. mcp
    mcp_p = subparsers.add_parser("mcp", help="Run Model Context Protocol stdio server")
    mcp_p.add_argument("--dir", default=".", help="Workspace root")

    return parser.parse_args(args)


def main(args_list: list[str] | None = None) -> None:
    args = parse_args(args_list)

    if not args.command:
        print("AgentGraph CLI — Standalone Cognitive Substrate & Knowledge Graph Engine")
        print("Run 'agentgraph --help' for available commands.")
        return

    if args.command == "init":
        target = Path(args.dir).resolve()
        print(f"[AgentGraph] Initializing workspace in {target}...")
        ag_dir = RepositoryInitializer.initialize_repository(target_dir=target, install_hooks=not args.no_hooks)
        print(f"  ✓ Initialized layout in {ag_dir}")
        print(f"[AgentGraph] Performing initial synchronization...")
        graph = RepositorySyncer.sync_repository(root_dir=target, db_path=ag_dir / "graph.db")
        stats = graph.get_stats()
        print(f"  ✓ Initial sync complete: {stats['total_nodes']} nodes, {stats['total_edges']} edges indexed.")

    elif args.command == "sync":
        target = Path(args.dir).resolve()
        db_path = Path(args.db)
        if not db_path.is_absolute():
            db_path = target / db_path
        print(f"[AgentGraph] Synchronizing workspace {target} into {db_path}...")
        graph = RepositorySyncer.sync_repository(root_dir=target, db_path=db_path)
        stats = graph.get_stats()
        print(f"  ✓ Sync complete: {stats['total_nodes']} nodes, {stats['total_edges']} edges in database.")

    elif args.command == "query":
        db_path = Path(args.db)
        graph = AgentGraphEngine(db_path=db_path)
        if db_path.exists():
            graph.load_from_db()
        else:
            print(f"[AgentGraph] Database {db_path} not found. Running sync...")
            graph = RepositorySyncer.sync_repository(db_path=db_path)

        results = graph.query(query_str=args.query_str, plane=args.plane, limit=args.limit)
        if args.json:
            print(json.dumps([r.to_dict() for r in results], indent=2))
        else:
            print(f"\n--- AgentGraph Search Results ({len(results)} found) ---")
            for idx, r in enumerate(results, 1):
                print(f"[{idx}] {r.node.label} ({r.node.id}) | Plane: {r.node.plane} | Type: {r.node.type} | Score: {r.score}")
                if r.node.content:
                    snippet = r.node.content[:100].replace("\n", " ")
                    print(f"    Content: {snippet}...")
            print()

    elif args.command == "traverse":
        db_path = Path(args.db)
        graph = AgentGraphEngine(db_path=db_path)
        if db_path.exists():
            graph.load_from_db()
        else:
            graph = RepositorySyncer.sync_repository(db_path=db_path)

        hops = graph.traverse(
            start_node_id=args.node_id,
            direction=args.direction,
            max_depth=args.depth,
            relation_filter=args.relation
        )
        if args.json:
            print(json.dumps(hops, indent=2))
        else:
            print(f"\n--- Traversal from '{args.node_id}' ({args.direction}, max depth {args.depth}) ---")
            for hop in hops:
                edge = hop.get("edge") or {}
                rel = edge.get("relation", "CONNECTED")
                src = edge.get("source", "")
                tgt = edge.get("target", "")
                print(f"  [Hop {hop['depth']}] {src} --[{rel}]--> {tgt}")
            print()

    elif args.command == "resolve":
        db_path = Path(args.db)
        graph = AgentGraphEngine(db_path=db_path)
        if db_path.exists():
            graph.load_from_db()
        else:
            graph = RepositorySyncer.sync_repository(db_path=db_path)

        deps = graph.resolve_dependencies(args.node_id)
        if args.json:
            print(json.dumps({"node_id": args.node_id, "dependencies": deps}, indent=2))
        else:
            print(f"\n--- Topological Dependencies for '{args.node_id}' ({len(deps)} items) ---")
            for idx, d in enumerate(deps, 1):
                node = graph.get_node(d)
                lbl = f" ({node.label})" if node else ""
                print(f"  {idx}. {d}{lbl}")
            print()

    elif args.command == "validate":
        target = Path(args.dir).resolve()
        db_path = Path(args.db)
        if not db_path.is_absolute():
            db_path = target / db_path

        graph = RepositorySyncer.sync_repository(root_dir=target, db_path=db_path)
        report = graph.validate()

        if args.json:
            print(json.dumps(report.to_dict(), indent=2))
        else:
            print("\n=== AgentGraph Topology Health Audit ===")
            print(f"Status: {'PASSED (Valid DAG)' if report.is_valid else 'DEGRADED (Issues Detected)'}")
            print(f"Total Nodes: {report.total_nodes} | Total Edges: {report.total_edges}")
            print(f"Plane Distribution: {json.dumps(report.plane_counts)}")
            print(f"Dangling Edges: {len(report.dangling_edges)}")
            if report.dangling_edges:
                for src, tgt in report.dangling_edges:
                    print(f"  ✗ Dangling: {src} -> {tgt}")
            print(f"Detected Cycles: {len(report.detected_cycles)}")
            if report.detected_cycles:
                for c in report.detected_cycles:
                    print(f"  ✗ Cycle: {' -> '.join(c)}")
            print()
            if not report.is_valid:
                sys.exit(1)

    elif args.command == "export":
        db_path = Path(args.db)
        graph = AgentGraphEngine(db_path=db_path)
        if db_path.exists():
            graph.load_from_db()
        else:
            graph = RepositorySyncer.sync_repository(db_path=db_path)

        if args.format == "mermaid":
            output_content = GraphExporter.to_mermaid(graph, plane=args.plane)
        elif args.format == "dot":
            output_content = GraphExporter.to_dot(graph, plane=args.plane)
        else:
            output_content = GraphExporter.to_json(graph)

        if args.out:
            out_path = Path(args.out).resolve()
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(output_content, encoding="utf-8")
            print(f"✓ Exported {args.format} to {out_path}")
        else:
            print(output_content)

    elif args.command == "stats":
        db_path = Path(args.db)
        graph = AgentGraphEngine(db_path=db_path)
        if db_path.exists():
            graph.load_from_db()
        else:
            graph = RepositorySyncer.sync_repository(db_path=db_path)

        stats = graph.get_stats()
        if args.json:
            print(json.dumps(stats, indent=2))
        else:
            print("\n=== AgentGraph Topological Metrics ===")
            print(f"Total Nodes: {stats['total_nodes']}")
            print(f"Total Edges: {stats['total_edges']}")
            print("Nodes per Plane:")
            for p, cnt in stats["plane_node_distribution"].items():
                print(f"  - {p}: {cnt}")
            print("Edges per Relation:")
            for r, cnt in stats["relation_distribution"].items():
                print(f"  - {r}: {cnt}")
            print()

    elif args.command == "quality-gate":
        target = Path(args.dir).resolve()
        db_path = Path(args.db)
        if not db_path.is_absolute():
            db_path = target / db_path

        print("=======================================================")
        print("  AgentGraph Quality Gates & Architecture Audit Suite")
        print("=======================================================\n")

        # Gate 1: Workspace & Sync Gate
        print("[Quality Gate 1/4] Synchronizing workspace substrate...")
        graph = RepositorySyncer.sync_repository(root_dir=target, db_path=db_path)
        print(f"  ✓ Gate 1 PASSED: {len(graph.nodes)} nodes, {len(graph.edges)} edges indexed.")

        # Gate 2: Graph Health & Cycle Gate
        print("[Quality Gate 2/4] Validating topology and detecting cycles...")
        report = graph.validate()
        if not report.is_valid:
            print(f"  ✗ Gate 2 FAILED: {len(report.detected_cycles)} cycles, {len(report.dangling_edges)} dangling edges.")
            sys.exit(1)
        print("  ✓ Gate 2 PASSED: 0 cycles, 0 dangling edges, DAG valid.")

        # Gate 3: Unit Test Suite Gate
        print("[Quality Gate 3/4] Running unit test verification suite...")
        import unittest
        loader = unittest.TestLoader()
        tests_dir = target / "tests"
        if tests_dir.exists():
            suite = loader.discover(str(tests_dir))
            runner = unittest.TextTestRunner(verbosity=0)
            res = runner.run(suite)
            if not res.wasSuccessful():
                print(f"  ✗ Gate 3 FAILED: {len(res.failures)} test failures, {len(res.errors)} errors.")
                sys.exit(1)
            print(f"  ✓ Gate 3 PASSED: {res.testsRun} unit tests passed cleanly.")
        else:
            print("  - Gate 3 SKIPPED: No tests/ directory.")

        # Gate 4: Build Package Gate
        print("[Quality Gate 4/4] Verifying build packages...")
        build_py = target / "scripts" / "build.py"
        if build_py.exists():
            import subprocess
            try:
                subprocess.run([sys.executable, str(build_py)], check=True, stdout=subprocess.DEVNULL)
                print("  ✓ Gate 4 PASSED: Standalone release package verified.")
            except Exception as b_err:
                print(f"  ✗ Gate 4 FAILED: Build script error: {b_err}")
                sys.exit(1)
        else:
            print("  - Gate 4 SKIPPED: No scripts/build.py.")

        if args.json:
            print(json.dumps({"status": "PASSED", "total_nodes": len(graph.nodes), "total_edges": len(graph.edges)}, indent=2))
        else:
            print("\n=======================================================")
            print("  AgentGraph Quality Gates: ALL GATES PASSED (100% Valid)")
            print("=======================================================\n")

    elif args.command == "mcp":
        run_mcp_server(workspace_dir=args.dir)


if __name__ == "__main__":
    main()
