import subprocess
import tempfile
import unittest
from pathlib import Path

from examples.git_reentry import classify_route, parse_porcelain, run_git_status


class GitReentryTests(unittest.TestCase):
    def test_large_dirty_tree_is_classified_from_full_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(
                ["git", "init", "-q"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            # Make status output comfortably larger than the 2,000-character
            # receipt tail. Put a code file first alphabetically so a tail-only
            # classifier could incorrectly see only docs files.
            (repo / "000_code.py").write_text("print('x')\n", encoding="utf-8")
            docs = repo / "docs"
            docs.mkdir()
            for i in range(180):
                (docs / f"very_long_document_name_{i:03d}.md").write_text(
                    "x\n", encoding="utf-8"
                )

            probe, full_text = run_git_status(repo)
            self.assertEqual(probe.returncode, 0)
            self.assertGreater(len(full_text), 2000)

            files = parse_porcelain(full_text)
            self.assertIn("000_code.py", files)
            self.assertEqual(classify_route(files), "code_or_mixed")

    def test_docs_only_route(self):
        self.assertEqual(
            classify_route(["README.md", "docs/guide.md"]),
            "docs",
        )

    def test_clean_route(self):
        self.assertEqual(classify_route([]), "clean")


if __name__ == "__main__":
    unittest.main()
