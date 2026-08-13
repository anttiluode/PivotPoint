#!/usr/bin/env python3
"""Real-command re-entry demo for PivotPoint.

This is intentionally mundane. It asks whether a small local decision can
avoid creating expensive measurements that cannot affect the next action.

Examples
--------

Pivot mode (conditionally run validation):

    python examples/git_reentry.py --repo . --test "python -m pytest -q"

Eager mode (always run supplied validation):

    python examples/git_reentry.py --repo . --test "python -m pytest -q" --mode eager

Docs can have a separate validator:

    python examples/git_reentry.py --repo . \
        --test "python -m pytest -q" \
        --docs-test "python -m mkdocs build --strict"

The script does NOT claim that its file classifier is intelligent. It is a
first wall-clock contact point. If hand-maintaining classification logic costs
more than the saved measurements, the branch should die.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import subprocess
import time
from typing import Iterable, List, Optional, Sequence, Tuple


DOC_EXTENSIONS = {
    ".md", ".mdx", ".rst", ".txt", ".adoc",
}
DOC_PREFIXES = (
    "docs/",
    "doc/",
)


@dataclass
class ProbeResult:
    name: str
    command: str
    seconds: float
    returncode: int
    stdout_tail: str
    stderr_tail: str


@dataclass
class ReentryResult:
    mode: str
    route: str
    changed_files: List[str]
    probes: List[ProbeResult]
    total_seconds: float
    recommendation: str


def run_command(
    command: Sequence[str] | str,
    *,
    cwd: Path,
    shell: bool = False,
    name: str,
) -> ProbeResult:
    start = time.perf_counter()
    cp = subprocess.run(
        command,
        cwd=str(cwd),
        shell=shell,
        capture_output=True,
        text=True,
        errors="replace",
    )
    seconds = time.perf_counter() - start
    shown = command if isinstance(command, str) else " ".join(command)
    return ProbeResult(
        name=name,
        command=shown,
        seconds=seconds,
        returncode=int(cp.returncode),
        stdout_tail=cp.stdout[-2000:],
        stderr_tail=cp.stderr[-2000:],
    )


def run_git_status(cwd: Path) -> Tuple[ProbeResult, str]:
    """Return a compact receipt *and* full porcelain text for routing.

    Validation command output is intentionally truncated in receipts, but git
    status is itself the cheap observation used to choose the route. Routing
    from a truncated tail silently loses files on large dirty trees, so the
    classifier must see the full status output.

    ``--untracked-files=all`` is also deliberate: otherwise Git may collapse an
    untracked directory to one ``?? directory/`` entry, hiding mixed file types
    inside the very observation used for routing.
    """
    command = ["git", "status", "--porcelain", "--untracked-files=all"]
    start = time.perf_counter()
    cp = subprocess.run(
        command,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        errors="replace",
    )
    seconds = time.perf_counter() - start
    probe = ProbeResult(
        name="git_status",
        command=" ".join(command),
        seconds=seconds,
        returncode=int(cp.returncode),
        stdout_tail=cp.stdout[-2000:],
        stderr_tail=cp.stderr[-2000:],
    )
    return probe, cp.stdout


def parse_porcelain(text: str) -> List[str]:
    files: List[str] = []
    for raw in text.splitlines():
        if len(raw) < 4:
            continue
        path = raw[3:].strip()
        # rename format: old -> new
        if " -> " in path:
            path = path.split(" -> ", 1)[1].strip()
        if path:
            files.append(path.replace("\\", "/"))
    return files


def is_doc_file(path: str) -> bool:
    p = path.lower().replace("\\", "/")
    if p.startswith(DOC_PREFIXES):
        return True
    return Path(p).suffix in DOC_EXTENSIONS


def classify_route(files: Iterable[str]) -> str:
    files = list(files)
    if not files:
        return "clean"
    if all(is_doc_file(p) for p in files):
        return "docs"
    return "code_or_mixed"


def recommendation(route: str, probes: List[ProbeResult]) -> str:
    failures = [p for p in probes if p.returncode != 0]
    if failures:
        return "measurement_failed_or_validation_failed"
    if route == "clean":
        return "resume_without_revalidation"
    if route == "docs":
        return "resume_docs_path"
    return "resume_code_path"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, default=Path("."))
    ap.add_argument(
        "--mode",
        choices=("pivot", "eager"),
        default="pivot",
        help="pivot runs only route-relevant validators; eager runs all supplied validators",
    )
    ap.add_argument(
        "--test",
        help="user-supplied code validation command; executed through the system shell",
    )
    ap.add_argument(
        "--docs-test",
        help="optional user-supplied docs validation command; executed through the system shell",
    )
    ap.add_argument("--json", type=Path, help="optional path for machine-readable result")
    args = ap.parse_args()

    repo = args.repo.resolve()
    probes: List[ProbeResult] = []
    t0 = time.perf_counter()

    status, status_text = run_git_status(repo)
    probes.append(status)
    if status.returncode != 0:
        result = ReentryResult(
            mode=args.mode,
            route="unknown",
            changed_files=[],
            probes=probes,
            total_seconds=time.perf_counter() - t0,
            recommendation="not_a_git_repo_or_git_failed",
        )
        print(json.dumps(asdict(result), indent=2))
        raise SystemExit(2)

    changed_files = parse_porcelain(status_text)
    route = classify_route(changed_files)

    if args.mode == "eager":
        commands: List[Tuple[str, Optional[str]]] = [
            ("code_validation", args.test),
            ("docs_validation", args.docs_test),
        ]
    elif route == "code_or_mixed":
        commands = [("code_validation", args.test)]
    elif route == "docs":
        commands = [("docs_validation", args.docs_test)]
    else:
        commands = []

    for name, command in commands:
        if not command:
            continue
        probes.append(
            run_command(
                command,
                cwd=repo,
                shell=True,
                name=name,
            )
        )

    result = ReentryResult(
        mode=args.mode,
        route=route,
        changed_files=changed_files,
        probes=probes,
        total_seconds=time.perf_counter() - t0,
        recommendation=recommendation(route, probes),
    )

    rendered = json.dumps(asdict(result), indent=2)
    print(rendered)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
