#!/usr/bin/env python3
"""Synchronize the skill's api-guide snapshot from the project api guide."""

from __future__ import annotations

import argparse
import filecmp
import shutil
from pathlib import Path


def copy_tree(source: Path, target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    for source_path in sorted(source.iterdir()):
        if source_path.name.startswith("."):
            continue
        target_path = target / source_path.name
        if source_path.is_dir():
            copy_tree(source_path, target_path)
        elif source_path.is_file():
            shutil.copy2(source_path, target_path)


def compare_tree(source: Path, target: Path) -> list[str]:
    diffs: list[str] = []
    source_files = {
        path.relative_to(source)
        for path in source.rglob("*")
        if path.is_file() and not any(part.startswith(".") for part in path.relative_to(source).parts)
    }
    target_files = {
        path.relative_to(target)
        for path in target.rglob("*")
        if path.is_file() and not any(part.startswith(".") for part in path.relative_to(target).parts)
    }
    for path in sorted(source_files - target_files):
        diffs.append(f"Only in source: {path}")
    for path in sorted(target_files - source_files):
        diffs.append(f"Only in target: {path}")
    for path in sorted(source_files & target_files):
        if not filecmp.cmp(source / path, target / path, shallow=False):
            diffs.append(f"Different: {path}")
    return diffs


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync or check skill api-guide snapshot.")
    parser.add_argument("--source", default="api指引", help="Project source api guide directory.")
    parser.add_argument(
        "--target",
        default="skill/ghostcut-api-guide/references/api-guide",
        help="Skill snapshot api-guide directory.",
    )
    parser.add_argument("--check", action="store_true", help="Only check whether source and target differ.")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    target = Path(args.target).resolve()
    if not source.is_dir():
        raise SystemExit(f"Source directory not found: {source}")
    if args.check:
        if not target.is_dir():
            raise SystemExit(f"Target directory not found: {target}")
        diffs = compare_tree(source, target)
        if diffs:
            print("\n".join(diffs))
            raise SystemExit(1)
        print("api-guide snapshot is in sync")
        return

    copy_tree(source, target)
    print(f"Synced {source} -> {target}")


if __name__ == "__main__":
    main()
