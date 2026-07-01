#!/usr/bin/env python3
"""Check or synchronize the skill's api-guide snapshot."""

from __future__ import annotations

import argparse
import filecmp
import re
import shutil
from pathlib import Path


MARKDOWN_LINK_RE = re.compile(r"\]\(\./([^)\s]+\.md)\)")


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


def validate_snapshot(target: Path) -> list[str]:
    problems: list[str] = []
    if not target.is_dir():
        return [f"Target directory not found: {target}"]
    index_path = target / "llms.txt"
    if not index_path.is_file():
        return [f"Missing snapshot index: {index_path.name}"]

    indexed_files = set(MARKDOWN_LINK_RE.findall(index_path.read_text(encoding="utf-8")))
    actual_files = {path.name for path in target.glob("*.md")}

    for filename in sorted(indexed_files - actual_files):
        if not (target / filename).is_file():
            problems.append(f"Missing snapshot file: {filename}")
    for filename in sorted(actual_files - indexed_files):
        problems.append(f"Unindexed snapshot file: {filename}")
    return problems


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync or check skill api-guide snapshot.")
    parser.add_argument(
        "--source",
        help="Optional external api-guide directory to compare or copy into the skill snapshot.",
    )
    parser.add_argument(
        "--target",
        default="skills/ghostcut-api-guide/references/api-guide",
        help="Skill snapshot api-guide directory.",
    )
    parser.add_argument("--check", action="store_true", help="Only check whether source and target differ.")
    args = parser.parse_args()

    target = Path(args.target).resolve()
    if args.source is None:
        if args.check:
            problems = validate_snapshot(target)
            if problems:
                print("\n".join(problems))
                raise SystemExit(1)
            print(f"api-guide snapshot is available: {target}")
            return
        parser.error("--source is required when syncing from an external api-guide directory")

    source = Path(args.source).resolve()
    if not source.is_dir():
        raise SystemExit(f"Source directory not found: {source}")
    if args.check:
        problems = validate_snapshot(target)
        if problems:
            print("\n".join(problems))
            raise SystemExit(1)
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
