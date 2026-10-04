"""Repository Initializer for AgentGraph file organization and workspace setup."""

from __future__ import annotations

import os
import stat
from pathlib import Path

from agentgraph.init.templates import (
    AGENTS_MD_TEMPLATE,
    CORE_INVARIANTS_JSON,
    DEFAULT_CONFIG_JSON,
    GRAPH_STANDARDS_JSON,
    KNOWLEDGE_ARCH_MD,
    PRE_COMMIT_HOOK_SCRIPT,
    ROLE_ARCHITECT_JSON,
    ROLE_DEVELOPER_JSON,
    ROLE_RESEARCHER_JSON,
    ROLE_REVIEWER_JSON,
    WORKFLOW_PIPELINE_JSON,
)


class RepositoryInitializer:
    """Scaffolds directory layout and populates default rules, roles, workflows, and knowledge."""

    @staticmethod
    def initialize_repository(target_dir: Path | str = ".", install_hooks: bool = True) -> Path:
        """Initialize AgentGraph layout in target_dir."""
        root = Path(target_dir).resolve()
        ag_dir = root / ".agentgraph"

        # 1. Scaffold directory hierarchy
        dirs = [
            ag_dir,
            ag_dir / "rules",
            ag_dir / "agents",
            ag_dir / "workflows",
            ag_dir / "knowledge",
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

        # 2. Write config.json
        config_path = ag_dir / "config.json"
        if not config_path.exists():
            config_path.write_text(DEFAULT_CONFIG_JSON, encoding="utf-8")

        # 3. Write default rule JSON templates
        rules_dir = ag_dir / "rules"
        (rules_dir / "10_core_invariants.json").write_text(CORE_INVARIANTS_JSON, encoding="utf-8")
        (rules_dir / "20_graph_standards.json").write_text(GRAPH_STANDARDS_JSON, encoding="utf-8")

        # 4. Write default agent role JSON templates
        agents_dir = ag_dir / "agents"
        (agents_dir / "architect.json").write_text(ROLE_ARCHITECT_JSON, encoding="utf-8")
        (agents_dir / "developer.json").write_text(ROLE_DEVELOPER_JSON, encoding="utf-8")
        (agents_dir / "reviewer.json").write_text(ROLE_REVIEWER_JSON, encoding="utf-8")
        (agents_dir / "researcher.json").write_text(ROLE_RESEARCHER_JSON, encoding="utf-8")

        # 5. Write default workflow JSON template
        workflows_dir = ag_dir / "workflows"
        (workflows_dir / "code_review_pipeline.json").write_text(WORKFLOW_PIPELINE_JSON, encoding="utf-8")

        # 6. Write default knowledge file
        knowledge_dir = ag_dir / "knowledge"
        (knowledge_dir / "architecture.md").write_text(KNOWLEDGE_ARCH_MD, encoding="utf-8")

        # 7. Write root AGENTS.md if missing
        agents_md_path = root / "AGENTS.md"
        if not agents_md_path.exists():
            agents_md_path.write_text(AGENTS_MD_TEMPLATE, encoding="utf-8")

        # 8. Install git pre-commit hook if requested
        if install_hooks:
            git_hooks_dir = root / ".git" / "hooks"
            if git_hooks_dir.exists():
                hook_path = git_hooks_dir / "pre-commit"
                hook_path.write_text(PRE_COMMIT_HOOK_SCRIPT, encoding="utf-8")
                st = os.stat(hook_path)
                os.chmod(hook_path, st.st_mode | stat.S_IEXEC)

        return ag_dir
