import unittest
from pathlib import Path

from examples.benchmark_git_reentry import compare


def run(total_seconds, probes, route="docs", recommendation="resume_docs_path"):
    return {
        "mode": "test",
        "route": route,
        "changed_files": ["docs/x.md"],
        "probes": [
            {
                "name": "git_status",
                "returncode": 0,
                "seconds": 0.01,
                "command": "git status --porcelain",
                "stdout_tail": "",
                "stderr_tail": "",
            },
            *probes,
        ],
        "total_seconds": total_seconds,
        "recommendation": recommendation,
    }


def probe(name, returncode=0):
    return {
        "name": name,
        "returncode": returncode,
        "seconds": 1.0,
        "command": name,
        "stdout_tail": "",
        "stderr_tail": "",
    }


class GateALogicTests(unittest.TestCase):
    def test_eager_only_failure_overrides_large_speedup(self):
        pivot = [run(1.0, [probe("docs_validation")])]
        eager = [
            run(
                100.0,
                [probe("code_validation", returncode=1), probe("docs_validation")],
                recommendation="measurement_failed_or_validation_failed",
            )
        ]

        result = compare(
            repo=Path("."),
            pivot_runs=pivot,
            eager_runs=eager,
            min_savings_fraction=0.10,
        )

        self.assertEqual(result.verdict, "unsafe_skip_observed")
        self.assertEqual(
            result.eager_failures_skipped_by_pivot,
            ["code_validation"],
        )
        self.assertGreater(result.median_fraction_saved, 0.90)

    def test_small_saving_is_not_promoted(self):
        pivot = [run(9.5, [probe("docs_validation")])]
        eager = [run(10.0, [probe("docs_validation")])]

        result = compare(
            repo=Path("."),
            pivot_runs=pivot,
            eager_runs=eager,
            min_savings_fraction=0.10,
        )

        self.assertEqual(result.verdict, "no_material_savings")

    def test_large_clean_saving_is_only_a_candidate(self):
        pivot = [run(4.0, [probe("docs_validation")])]
        eager = [
            run(10.0, [probe("code_validation"), probe("docs_validation")])
        ]

        result = compare(
            repo=Path("."),
            pivot_runs=pivot,
            eager_runs=eager,
            min_savings_fraction=0.10,
        )

        self.assertEqual(result.verdict, "candidate_savings")
        self.assertEqual(result.eager_failures_skipped_by_pivot, [])


if __name__ == "__main__":
    unittest.main()
