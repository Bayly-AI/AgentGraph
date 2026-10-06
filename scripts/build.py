#!/usr/bin/env python3
"""Build script for AgentGraph CLI releases in ./release/python/cli."""

import os
import shutil
import subprocess
import sys
import zipapp
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
RELEASE_DIR = ROOT_DIR / "release" / "python" / "cli"
BUILD_DIR = ROOT_DIR / "build"


def clean_release_dir():
    if RELEASE_DIR.exists():
        shutil.rmtree(RELEASE_DIR)
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)


def build_wheel_and_sdist():
    print("[AgentGraph Build] Building wheel and sdist packages...")
    cmd = [
        sys.executable,
        "setup.py",
        "sdist",
        "bdist_wheel",
        "--dist-dir",
        str(RELEASE_DIR),
    ]
    subprocess.run(cmd, cwd=ROOT_DIR, check=True)


def build_zipapp_executable():
    print("[AgentGraph Build] Building standalone executable CLI zipapp...")
    staging_dir = BUILD_DIR / "zipapp_staging"
    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    staging_dir.mkdir(parents=True, exist_ok=True)

    # Copy agentgraph package into staging
    shutil.copytree(ROOT_DIR / "agentgraph", staging_dir / "agentgraph")

    # Write root __main__.py in staging
    main_py = staging_dir / "__main__.py"
    main_py.write_text(
        "import sys\n"
        "from agentgraph.cli import main\n"
        "if __name__ == '__main__':\n"
        "    main()\n",
        encoding="utf-8"
    )

    output_exe = RELEASE_DIR / "agentgraph"
    zipapp.create_archive(
        source=staging_dir,
        target=output_exe,
        interpreter="/usr/bin/env python3"
    )
    # Make executable
    st = os.stat(output_exe)
    os.chmod(output_exe, st.st_mode | 0o755)
    print(f"[AgentGraph Build] Standalone executable created at {output_exe}")


def bundle_documentation():
    print("[AgentGraph Build] Bundling complete documentation set into release folder...")
    rel_docs_dir = RELEASE_DIR / "docs"
    if rel_docs_dir.exists():
        shutil.rmtree(rel_docs_dir)
    rel_docs_dir.mkdir(parents=True, exist_ok=True)

    # Copy docs tree
    if (ROOT_DIR / "docs").exists():
        shutil.copytree(ROOT_DIR / "docs", rel_docs_dir, dirs_exist_ok=True)

    # Copy root markdown documentation files
    for md_file in ["README.md", "README.TECHNICAL.md", "AGENTS.md", "LICENSE", "CONTRIBUTING.md", "SECURITY.md"]:
        src = ROOT_DIR / md_file
        if src.exists():
            shutil.copy2(src, RELEASE_DIR / md_file)

    # Create tar.gz and zip archives of the complete documentation set
    docs_archive_base = RELEASE_DIR / "AgentGraph-Documentation-1.0.0"
    shutil.make_archive(str(docs_archive_base), "gztar", root_dir=RELEASE_DIR, base_dir="docs")
    shutil.make_archive(str(docs_archive_base), "zip", root_dir=RELEASE_DIR, base_dir="docs")
    print(f"[AgentGraph Build] Documentation release archives created at {RELEASE_DIR}")


def main():
    clean_release_dir()
    build_wheel_and_sdist()
    build_zipapp_executable()
    bundle_documentation()

    print(f"\n[AgentGraph Build Success] Artifacts built in {RELEASE_DIR}:")
    for f in sorted(RELEASE_DIR.rglob("*")):
        if f.is_file():
            size_kb = f.stat().st_size / 1024
            rel_name = f.relative_to(RELEASE_DIR)
            print(f"  - {rel_name} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
