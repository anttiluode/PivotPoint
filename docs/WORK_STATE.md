# Unfinished work is not a delayed message

This distinction is now explicit in code because it is easy to erase in prose.

## Two different temporal objects

`PivotRuntime.Signal` means:

```text
a payload already exists
        ↓
it has been emitted
        ↓
it is traversing a route / delay
        ↓
it is not readable by the receiver yet
```

`WorkRegistry.WorkItem` means something different:

```text
a computation / measurement / request has begun
        ↓
its result may literally not exist yet
        ↓
it can succeed / fail / be cancelled
        ↓
if it succeeds, the result can exist but remain unread
        ↓
it is finally consumed by its intended receiver
```

Those two cases can produce the same completed transcript while requiring different next actions.

A controller that cannot distinguish:

```text
no refresh requested
```

from:

```text
refresh already running, result not born yet
```

has an observation problem before it has a reasoning problem.

## Why a separate registry

Do not hide process state inside a giant context blob.

The registry makes these lifecycle stages inspectable:

```text
PENDING
SUCCEEDED
FAILED
CANCELLED
CONSUMED
```

and keeps owner/target identity explicit.

`local_state(node, now)` is deliberately not a global process table. A node sees only work it owns or work intended for it. Experiments may grant broader visibility, but that permission must be explicit.

## AsyncWorkerPool is not the invention

`pivotpoint/workers.py` uses ordinary Python `asyncio` to run real awaitables.

That is a baseline-quality mechanism, not a PivotPoint result.

Its purpose is only to keep the explicit work state synchronized with real computation so experiments can contain genuine situations such as:

```text
fast result available and consumed
while
slow result is still computing
```

or:

```text
worker failed
while
another route remains usable
```

The result payload does not exist in the registry before the worker completes.

## The important architectural question

The interesting question is not whether asynchronous work is possible. It obviously is.

The question is whether a system benefits from making the following small local state first-class:

```text
what is readable now
what I already asked for
what is still becoming
what just became readable
what failed
what I can cancel / probe / wait for / route around
what those interventions are expected to unlock next
```

That state can then be offered to a tiny local control policy without requiring a synchronized reconstruction of every worker and memory in the system.

## Baselines that must be allowed to win

PivotPoint does not get credit for rediscovering any of these:

- `asyncio` / futures / promises;
- a priority queue;
- a behavior tree;
- a workflow engine;
- build-system dependency graphs;
- value-of-information / optimal stopping;
- an ordinary agent framework that stores pending tool calls;
- a transformer supplied with the same compact live-state snapshot.

The architecture only earns complexity if held-out tasks show an advantage after those baselines receive the same information and budget.

## Lesson imported from FunctionalArbors

The FunctionalArbors line eventually showed a useful failure: delayed credit transport could work while free structural credit assignment still failed. Knowing which branch was recently active was not enough to know which structural event caused the useful outcome.

Carry that warning here.

If PivotPoint later grows routes, do **not** reward a branch merely because:

```text
pivot unresolved
+ branch active nearby
+ later success
```

A stronger structural mark should measure what the intervention actually changed, for example:

```text
before intervention: reachable/readable set R_before

after intervention:  reachable/readable set R_after

causal candidate mark ~ R_after - R_before
```

with matched controls / replay / counterfactual approximations where possible.

In other words:

> structural growth should be credited for measured change in control/accessibility, not proximity to reward.

Do not implement this growth gate until the simpler re-entry, async, and dynamic-effectome gates have earned continuation.

## Current next contact

1. Run `examples/benchmark_git_reentry.py` on realistic interrupted repositories and keep the receipts, including unsafe skips.
2. Build the asynchronous held-out gate around **real** worker completion states.
3. Compare the local PivotPoint view against a boring global scheduler and a compact full live-state snapshot.
4. Only then ask whether modulators / heterogeneous effectome state improve adaptation.
