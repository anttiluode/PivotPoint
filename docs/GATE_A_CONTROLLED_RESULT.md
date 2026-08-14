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

## The harder baseline problem

The controlled benchmark used **eager validation** as the only baseline. That is too weak for file-derived work.

For work whose validity is a function of repository inputs, a dependency-aware/content-addressed build or test cache can often make the same decision more precisely:

```text
docs-only change
    -> validator inputs unchanged
    -> reuse prior verified result

code change affecting only a subset
    -> invalidate only dependent work
```

The present PivotPoint classifier is coarser:

```text
clean / docs / code_or_mixed
```

so on file-derived validation it has no demonstrated structural advantage over a verified dependency-aware cache and can be strictly worse on partial code changes.

Do **not** claim that caching has zero unsafe-skip risk "by construction" in all real systems: undeclared dependencies, non-hermetic tests, environment state, network state and flakiness can also defeat caches. The correct conclusion is narrower and stronger:

> **When the expensive question is determined by declared/versioned file inputs, PivotPoint's current filename policy is not the right competitor. Ordinary dependency tracking is the baseline to beat.**

Making the test suite slower would not repair this benchmark; it would simply make the value of correct caching larger.

## Verdict

```text
CONTROLLED_HARNESS_BEHAVES_AS_SPECIFIED
FILE_STATE_REENTRY_NOT_YET_COMPETITIVE_WITH_DEPENDENCY_CACHE
REAL_GATE_A_STILL_OPEN
```

No `unsafe_skip_observed` occurred in these three controlled states.

This does **not** promote the re-entry branch.

## Where Gate A should move

The next discriminating test should use expensive state that is **not reducible to a hash of the repository tree**:

- work already in flight;
- remote result completed but not yet consumed;
- transient network failure versus terminal failure;
- another worker/process still producing an artifact;
- external status that can change while the tree stays fixed.

This is also the state class represented by `pivotpoint/work.py`: `PENDING`, `SUCCEEDED` but unread, `FAILED`, `CANCELLED`, and `CONSUMED`.

A good concrete testbed already exists in `GeometricNeuronV22`: morphology recovery performs real Allen/NeuroMorpho requests, has real latency, successful remote results, and at least one published identifier that remains unresolved. Reissuing every request after interruption is waste; blindly trusting a local tree hash cannot tell whether a request is still in flight, has just completed elsewhere, or failed remotely.

However, the strong baseline there is **not eager refetch**. It is an ordinary durable job/request ledger with idempotency plus whatever HTTP conditional caching the source supports. If PivotPoint cannot outperform or simplify that baseline, then the distinct language has not bought an engineering product; it has rediscovered workflow orchestration.

That is the next honest gate.
