# Gate A — real task re-entry

This gate exists to stop the first PivotPoint product idea from surviving on assigned toy costs.

## Question

After an interruption, can a small cheap local inspection avoid expensive verification that cannot affect the next action **without hiding failures that eager verification would have found**?

The current candidate is deliberately mundane:

```text
read cheap recorded state
        ↓
classify the current route
        ↓
run only route-relevant expensive probes
```

The baseline is equally mundane:

```text
run every supplied validator eagerly
```

There is no claim of a new scheduling algorithm here. This is a cost gate for one concrete use of the PivotPoint idea.

## Runner

Use a realistic interrupted working tree, not a clean checkout:

```bash
python examples/benchmark_git_reentry.py \
    --repo . \
    --test "python -m pytest -q" \
    --docs-test "python -m mkdocs build --strict" \
    --repeats 5 \
    --json gate_a.json
```

For PivotPoint itself:

```bash
python examples/benchmark_git_reentry.py \
    --repo . \
    --test "python -m unittest discover -s tests -v" \
    --repeats 5
```

A clean tree will usually route to `clean` and is not an interesting re-entry episode. Run this while a real project is paused in a state you would genuinely want an agent to recover from.

## What is measured

The benchmark runs both modes against the same working tree and records real wall-clock time:

- `pivot`: only route-relevant supplied validators run;
- `eager`: every supplied validator runs.

Run order alternates each repeat to reduce systematic cache/warm-up advantage.

The receipt records:

- median/min/max wall-clock;
- validators actually executed;
- validation failures;
- route and recommendation;
- median seconds and fraction saved.

## The important adversarial rule

A skipped measurement does not count as a saving if it concealed a real failure.

If eager mode observes a failing validator that pivot mode never ran, the verdict is:

```text
unsafe_skip_observed
```

This overrides wall-clock savings.

That is the first thing to look for.

## Current classifier is intentionally weak

`git_reentry.py` currently distinguishes only:

```text
clean
docs
code_or_mixed
```

using changed filenames.

This is not intelligence. It is a cheap policy whose maintenance burden must be counted against any saved compute.

Projects where documentation can execute code, generated files affect packaging, notebooks produce artifacts, configuration changes alter tests, etc. can defeat such a classifier. Good. Those are exactly the cases that should stop a simplistic pivot policy from being promoted.

## Kill criteria

Kill or sharply downgrade the re-entry product branch if any of these dominate realistic runs:

1. eager-only failures are observed with non-trivial frequency;
2. median savings are small relative to validator/runtime noise;
3. project-specific classification rules become large or fragile;
4. a compact verified snapshot is as cheap and more reliable;
5. maintaining the routing schema costs more than the avoided probes;
6. ordinary build-system dependency information solves the same problem more safely.

The CLI uses a configurable default `--min-savings-fraction 0.10`. Ten percent is not a scientific threshold; it is merely a visible engineering line that prevents a 2% timing wobble from being narrated as a product win.

## What would count as a useful result

Not one cherry-picked repository.

A useful receipt set would contain several real projects with different expensive operations, for example:

- unit/integration tests;
- video render or model inference;
- static site/docs validation;
- large data preprocessing;
- network-backed verification;
- compilation/build steps.

For each interrupted episode, retain the full JSON receipt, including failures.

A positive outcome would look like:

```text
substantial median saved wall-clock / compute
+ no systematic eager-only failures
+ small stable routing logic
```

A negative outcome is equally useful:

```text
small savings
or unsafe skipped failures
or routing logic turns into a second build system
```

In that case Gate A has done its job and PivotPoint should move to the asynchronous-worker gate instead of polishing re-entry vocabulary.
