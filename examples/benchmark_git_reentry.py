#!/usr/bin/env python3
"""Benchmark PivotPoint git re-entry against eager verification.

This harness runs the existing ``git_reentry.py`` policy repeatedly on the
*current real working tree*.  It does not assign synthetic command costs.
Whatever test/render/build commands the caller supplies are actually executed
and timed.

Most importantly, eager verification is allowed to falsify the pivot route. If
eager mode observes a failing validator that pivot mode skipped, the run is
reported as ``unsafe_skip_observed`` even if pivot was much faster.

Example (Windows or POSIX shell quoting as appropriate):

    python examples/benchmark_git_reentry.py \
        --repo . \
        --test "python -m unittest discover -s tests -v" \
        --repeats 3

For a project with a separate docs validator:

    python examples/benchmark_git_reentry.py \
        --repo . \
        --test "python -m pytest -q" \
        --docs-test "python -m mkdocs build --strict" \
        --repeats 5 \
        --json gate_a.json

Run it on a realistic interrupted working tree. A clean checkout is not a useful
re-entry episode.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import statistics
import subprocess
import sys
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set


@dataclass
class ModeSummary:
    mode: str
    repeats: int
    median_seconds: float
    min_seconds: float
    max_seconds: float
    median_probe_count: float
    routes: List[str]
    recommendations: List[str]
    validator_failure_counts: Dict[str, int]
    probe_names: List[str]


@dataclass
class GateAResult:
    repo: str
    repeats: int
    pivot: ModeSummary
    eager: ModeSummary
    median_seconds_saved: float
    median_fraction_saved: Optional[float]
    eager_failures_skipped_by_pivot: List[str]
    verdict: str
    min_savings_fraction: float
    raw_runs: Dict[str, List[Dict[str, Any]]]


def _runner_path() -> Path:
    return Path(__file__).with_name("git_reentry.py").resolve()


def _build_command(
    *,
    mode: str,
    repo: Path,
    test: Optional[str],
    docs_test: Optional[str],
) -> List[str]:
    command = [
        sys.executable,
        str(_runner_path()),
        "--repo",
        str(repo),
        "--mode",
        mode,
    ]
    if test:
        command += ["--test", test]
    if docs_test:
        command += ["--docs-test", docs_test]
    return command


def run_once(
    *,
    mode: str,
    repo: Path,
    test: Optional[str],
    docs_test: Optional[str],
) -> Dict[str, Any]:
    cp = subprocess.run(
        _build_command(mode=mode, repo=repo, test=test, docs_test=docs_test),
        capture_output=True,
        text=True,
        errors="replace",
    )
    try:
        payload = json.loads(cp.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"git_reentry.py returned non-JSON output in {mode} mode\n"
            f"returncode={cp.returncode}\nstdout={cp.stdout[-2000:]}\n"
            f"stderr={cp.stderr[-2000:]}"
        ) from exc

    if cp.returncode != 0:
        raise RuntimeError(
            f"git_reentry.py failed in {mode} mode with code {cp.returncode}: "
            f"{payload.get('recommendation', 'unknown')}"
        )
    return payload


def _validator_failures(run: Mapping[str, Any]) -> Set[str]:
    return {
        str(probe.get("name"))
        for probe in run.get("probes", [])
        if probe.get("name") != "git_status" and int(probe.get("returncode", 0)) != 0
    }


def _probe_names(runs: Iterable[Mapping[str, Any]]) -> Set[str]:
    names: Set[str] = set()
    for run in runs:
        for probe in run.get("probes", []):
            name = str(probe.get("name"))
            if name != "git_status":
                names.add(name)
    return names


def summarize(mode: str, runs: Sequence[Mapping[str, Any]]) -> ModeSummary:
    if not runs:
        raise ValueError("at least one run is required")

    seconds = [float(run["total_seconds"]) for run in runs]
    probe_counts = [
        sum(1 for probe in run.get("probes", []) if probe.get("name") != "git_status")
        for run in runs
    ]
    failure_counts: Counter[str] = Counter()
    for run in runs:
        failure_counts.update(_validator_failures(run))

    return ModeSummary(
        mode=mode,
        repeats=len(runs),
        median_seconds=float(statistics.median(seconds)),
        min_seconds=float(min(seconds)),
        max_seconds=float(max(seconds)),
        median_probe_count=float(statistics.median(probe_counts)),
        routes=sorted({str(run.get("route", "unknown")) for run in runs}),
        recommendations=sorted(
            {str(run.get("recommendation", "unknown")) for run in runs}
        ),
        validator_failure_counts=dict(sorted(failure_counts.items())),
        probe_names=sorted(_probe_names(runs)),
    )


def compare(
    *,
    repo: Path,
    pivot_runs: Sequence[Mapping[str, Any]],
    eager_runs: Sequence[Mapping[str, Any]],
    min_savings_fraction: float,
) -> GateAResult:
    pivot = summarize("pivot", pivot_runs)
    eager = summarize("eager", eager_runs)

    eager_failure_names = set(eager.validator_failure_counts)
    pivot_probe_names = set(pivot.probe_names)
    skipped_failures = sorted(eager_failure_names - pivot_probe_names)

    seconds_saved = eager.median_seconds - pivot.median_seconds
    fraction_saved = (
        seconds_saved / eager.median_seconds if eager.median_seconds > 0 else None
    )

    if skipped_failures:
        verdict = "unsafe_skip_observed"
    elif eager.validator_failure_counts:
        # Both policies may have run the failing validator. This is not a speed win;
        # the episode is primarily telling us that the working tree is invalid.
        verdict = "validation_failure_observed"
    elif fraction_saved is None:
        verdict = "uninformative_zero_time"
    elif fraction_saved < min_savings_fraction:
        verdict = "no_material_savings"
    else:
        verdict = "candidate_savings"

    return GateAResult(
        repo=str(repo),
        repeats=len(pivot_runs),
        pivot=pivot,
        eager=eager,
        median_seconds_saved=float(seconds_saved),
        median_fraction_saved=(
            None if fraction_saved is None else float(fraction_saved)
        ),
        eager_failures_skipped_by_pivot=skipped_failures,
        verdict=verdict,
        min_savings_fraction=float(min_savings_fraction),
        raw_runs={
            "pivot": [dict(run) for run in pivot_runs],
            "eager": [dict(run) for run in eager_runs],
        },
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, default=Path("."))
    ap.add_argument("--test", help="code validator passed to git_reentry.py")
    ap.add_argument("--docs-test", help="docs validator passed to git_reentry.py")
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument(
        "--min-savings-fraction",
        type=float,
        default=0.10,
        help="below this median fractional wall-clock saving, Gate A is not a win",
    )
    ap.add_argument("--json", type=Path, help="optional path for full JSON receipt")
    args = ap.parse_args()

    if args.repeats < 1:
        raise SystemExit("--repeats must be >= 1")
    if not 0.0 <= args.min_savings_fraction <= 1.0:
        raise SystemExit("--min-savings-fraction must be in [0, 1]")

    repo = args.repo.resolve()
    pivot_runs: List[Dict[str, Any]] = []
    eager_runs: List[Dict[str, Any]] = []

    # Alternate modes to reduce slow drift / cache warming from favoring one mode.
    for i in range(args.repeats):
        order = ("pivot", "eager") if i % 2 == 0 else ("eager", "pivot")
        for mode in order:
            run = run_once(
                mode=mode,
                repo=repo,
                test=args.test,
                docs_test=args.docs_test,
            )
            if mode == "pivot":
                pivot_runs.append(run)
            else:
                eager_runs.append(run)

    result = compare(
        repo=repo,
        pivot_runs=pivot_runs,
        eager_runs=eager_runs,
        min_savings_fraction=args.min_savings_fraction,
    )
    rendered = json.dumps(asdict(result), indent=2)
    print(rendered)

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
