# Gate A — external-state re-entry

Status: **next discriminating gate; not yet run**

The first controlled Git re-entry benchmark only showed that the harness works. Its eager baseline was too weak for file-derived work: dependency-aware caching can often make the same skip decision more safely and more precisely.

This gate moves to the state class PivotPoint actually claims to make first-class:

```text
nothing requested
work pending / result not yet readable
work succeeded / result unread
work failed
result consumed
```

Those states are not, in general, functions of the repository tree.

## Concrete taskbed

Use `anttiluode/GeometricNeuronV22` morphology recovery as the first external taskbed.

Why it is suitable:

- recovery performs real network-backed requests;
- successful requests have nonzero latency and produce artifacts;
- some identifiers resolve and one published Allen identifier has remained unresolved;
- reissuing completed or still-running work is measurable waste;
- terminal/unresolved failure must not be mistaken for a request that merely has not completed yet.

The task is not to improve morphology science. It is to test re-entry control using work whose state lives partly outside the Git tree.

## Important implementation blocker

`pivotpoint/work.py` currently stores `WorkRegistry` state **in memory only** and deliberately does not run jobs.

Therefore it does not yet support literal controller-process restart/re-entry. Before this gate is run, add the smallest possible durable receipt format needed to restore:

```text
work_id
kind / source / target
started_at
status
remote or local job identity if available
artifact identity/hash if completed
error class if failed
consumed_at if consumed
```

Do not turn this into a large workflow engine before the gate. If minimal persistence immediately expands into a general scheduler/database, count that complexity against PivotPoint.

## Frozen episode classes

The benchmark must contain at least these re-entry states:

```text
N  NOT_STARTED
P  PENDING
U  SUCCEEDED_UNREAD
R  RETRYABLE_FAILURE
T  TERMINAL_OR_UNRESOLVED_FAILURE
C  CONSUMED
```

For every episode, the next correct action is defined before timing:

```text
N -> start
P -> wait / inspect job status; do not duplicate blindly
U -> consume existing result; do not refetch
R -> retry according to fixed retry rule
T -> stop/escalate; do not loop retries indefinitely
C -> continue downstream; do not refetch
```

## Policies

### EAGER_REFETCH

After re-entry, issue the remote operation again unless the downstream step is already complete.

This is intentionally weak and is retained only as a sanity baseline.

### ARTIFACT_CACHE

If a valid local result artifact exists, reuse it; otherwise issue the request.

Use conditional HTTP requests / ETag / Last-Modified information when the remote source provides them. Do not cripple the cache baseline.

This baseline handles `U` and `C` well but may not distinguish `N` from `P` if no completed artifact exists yet.

### DURABLE_LEDGER

An ordinary persistent request/job state machine with idempotency:

```text
not-started / pending / succeeded / failed / consumed
```

It may remember remote job/request identity, retry count and produced artifact.

This is the **strong product baseline**. If PivotPoint reduces to this baseline with different vocabulary, record that plainly.

### PIVOT_LOCAL

Use only receiver-local process-present state derived from PivotPoint's durable work receipt plus fixed action rules. It does not receive a global omniscient scheduler state unless the strong baseline receives the same information.

No model/LLM is needed for this first gate.

## Primary safety metric

For every episode, record whether the policy selected an action that could hide or destroy a correct result, create an unsafe duplicate side effect, or fail to retry a retryable operation.

Any systematic safety disadvantage is a failure regardless of speed.

For read-only morphology GET requests, duplicate requests are mainly a cost/latency error rather than a destructive side effect. The gate should therefore later be repeated on at least one idempotency-sensitive external action before any broad product claim.

## Primary cost metrics

Per episode and policy:

- number of remote requests started after re-entry;
- duplicate remote requests;
- wall-clock to correct next action;
- wall-clock to usable result when a result is required;
- bytes transferred where observable;
- retries;
- terminal failures retried unnecessarily;
- stale/incorrect artifacts consumed;
- persistent state size / rule complexity.

Report absolute seconds and request counts, not only percentages.

## First pass criterion — does process-present state matter beyond artifact caching?

The Pivot/state-aware policy earns a **concept-level** positive only if, across preregistered `P/U/R/T` episodes:

1. it makes fewer unnecessary remote requests than `ARTIFACT_CACHE`;
2. it reaches the correct next action faster in aggregate;
3. it has no higher unsafe-action rate;
4. the advantage comes specifically from distinguishing pending/unread/failure state, not from a hidden file-derived shortcut.

Otherwise the three-way/not-yet distinction has not earned an engineering consequence in this taskbed.

## Product criterion — does PivotPoint beat ordinary workflow state?

Even if the concept-level comparison passes, PivotPoint is **not** promoted as a distinct product unless it also shows a material advantage over `DURABLE_LEDGER` in at least one externally meaningful dimension without giving up safety:

- lower coordination/state cost;
- lower latency;
- fewer remote operations;
- better locality/scalability under multiple workers;
- simpler fixed control logic at equal capability.

If `PIVOT_LOCAL` and `DURABLE_LEDGER` are behaviorally equivalent and similarly complex, the verdict is:

```text
PROCESS_PRESENT_STATE_USEFUL
PIVOTPOINT_NOT_DISTINCT_FROM_DURABLE_WORKFLOW_STATE
```

That is a valid and valuable result.

## Kill / downgrade conditions

Downgrade the external re-entry product branch if any dominate:

1. artifact/HTTP caching captures essentially all savings;
2. a durable job ledger matches PivotPoint exactly;
3. persistence/routing logic grows into a second workflow engine;
4. remote-state polling costs as much as simply performing the operation;
5. failures or stale state cause unsafe skips/retries;
6. the only positive episodes depend on contrived sleep delays rather than real external operations.

## Why this is the right next gate

The Git benchmark tested a static-file classifier. This gate tests the more characteristic claim in `work.py`:

> `PENDING` is not `SUCCEEDED but unread`, and neither is `nothing has been requested`.

If that distinction cannot change the correct next action cheaply on real external work, PivotPoint should stop building around it.

If it can, the next question is whether the result is anything more than ordinary durable workflow bookkeeping.
