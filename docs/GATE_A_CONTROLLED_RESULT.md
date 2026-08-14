# Gate A — first controlled PivotPoint receipt

Date: 2026-08-14

Workflow: `.github/workflows/gate-a-controlled.yml`

GitHub Actions run: `31784675693`

Artifact: `gate-a-pivotpoint-receipts`

## Scope

This is a **controlled smoke test of the Gate A harness on PivotPoint itself**, not the realistic product gate requested in `GATE_A_REAL_REENTRY.md`.

The workflow used the repository's real unit-test command and three disposable checkout states:

1. clean checkout;
2. a docs-only dirty state created by appending a harmless HTML comment to `docs/WORK_STATE.md`;
3. a code-only dirty state created by appending a harmless Python comment to `pivotpoint/core.py`.

The dirty states are synthetic. The validator is also tiny: the 18-unit-test suite reports roughly 0.03 s of test execution and about 0.26-0.27 s end-to-end subprocess time. Therefore percentage savings here are not a product result.

## Results

### Clean control

```text
pivot median      0.002662 s
  validators      0

eager median      0.268848 s
  validators      code_validation

saved median       0.266186 s
fraction saved     99.01 %
eager-only failures none
harness verdict    candidate_savings
```

Interpretation: expected and uninteresting. A clean worktree is explicitly not the intended Gate A episode.

### Controlled docs-only dirty state

```text
route              docs
changed file       docs/WORK_STATE.md

pivot median       0.002682 s
  validators       0

eager median       0.272099 s
  validators       code_validation

saved median       0.269417 s
fraction saved     99.01 %
eager-only failures none
harness verdict    candidate_savings
```

Interpretation: the current classifier does what it says it does. For a docs-only change, it avoids the supplied code validator. Eager validation found no hidden failure. Because the suite costs only about a quarter second, this is a routing sanity check, not evidence of useful product economics.

### Controlled code-only dirty state

```text
route              code_or_mixed
changed file       pivotpoint/core.py

pivot median       0.267556 s
  validators       code_validation

eager median       0.265709 s
  validators       code_validation

saved median      -0.001847 s
fraction saved    -0.70 %
eager-only failures none
harness verdict    no_material_savings
```

Interpretation: expected. When code is dirty, both policies run the same validator and PivotPoint buys nothing except a few milliseconds of noise.

## Verdict

```text
CONTROLLED_HARNESS_BEHAVES_AS_SPECIFIED
REAL_GATE_A_STILL_OPEN
```

No `unsafe_skip_observed` occurred in these three controlled states.

This does **not** promote the re-entry branch. The real gate still requires realistic interrupted worktrees with validators expensive enough that skipping one matters, and it must retain failures as aggressively as savings.

The important next receipt is not another synthetic PivotPoint edit. It is a genuine dirty project state with a real slow build/test/render/inference step. If those receipts show small absolute savings, eager-only failures, or project-specific routing logic expanding into a second build system, the branch should die or be downgraded exactly as preregistered.
