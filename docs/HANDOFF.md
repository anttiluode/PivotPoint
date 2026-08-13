# HANDOFF — read this first on reboot

## One-sentence state

**PivotPoint is an attempt to build intelligence around a small local causal branching surface: choose an action now that changes what will become readable next.**

Do not restart from “how wide is the present?” and do not rename the core object unless data forces it.

---

## The current decomposition

Keep these questions separate:

1. **existence** — does a useful trace/result/state exist at all?
2. **access** — is it readable by this receiver now?
3. **unfinished work** — has a process begun whose result does not exist yet?
4. **reachable accessibility** — what available action/trajectory could make useful state readable next?
5. **control** — if readable, can it actually alter behavior/system state?

The repo is mainly about #3 and #4 while treating #1/#2/#5 as constraints.

The central question remains:

> **CONTROL: what can I do now that changes what I will be able to read next?**

---

## Core vocabulary — keep stable

### PivotPoint
A local state where materially different future readouts are reachable through currently feasible actions.

### Nominal option
An action that can be represented or named.

### Effective option
An action whose required downstream route is currently open enough to materially alter future state/accessibility.

### Wiring
Potential communication graph.

### Effectome
Current effective influence graph after gates, modulators, receiver state, occupancy, resource constraints, etc.

### Modulator
A slower control signal that changes gain/threshold/persistence/routing/plasticity rather than carrying the task content itself.

### Reachable accessibility
What can become readable next under actions/trajectories available from the current local state.

### Control degrees of freedom
The effective number/dimension of materially different reachable futures, not the raw count of named actions.

### Signal
A payload already exists but is delayed/in flight to a receiver.

### WorkItem
A process has started but its result may literally not exist yet. Lifecycle: `PENDING -> SUCCEEDED/FAILED/CANCELLED`, with successful results remaining unread until `CONSUMED`.

---

## What exists now

### `pivotpoint/core.py`
Minimal substrate for:

- delayed signals;
- local inboxes;
- fixed wiring;
- modulated effective edge gain;
- transparent action offers and a deliberately boring PivotPolicy.

### `pivotpoint/work.py`
Explicit process-present state:

- owner and intended target;
- pending work;
- optional ETA;
- success/failure/cancellation;
- successful-but-unconsumed results;
- local visibility rather than a global process table.

Important distinction:

```text
Signal:
    payload exists, route unfinished

WorkItem:
    computation itself unfinished; payload may not exist yet
```

### `pivotpoint/workers.py`
Minimal `asyncio` adapter that mirrors **real** unfinished awaitables into `WorkRegistry`.

This is not claimed as a new scheduler. `asyncio` is the baseline mechanism. Tests establish only lifecycle semantics: a fast result can become readable while a slow worker remains genuinely pending; failure and cancellation become explicit state.

### `examples/git_reentry.py`
First mundane product contact: inspect cheap git state and conditionally run expensive validation.

### `examples/benchmark_git_reentry.py`
Gate A wall-clock harness. It compares pivot vs eager verification on the current real working tree, alternates run order, and lets eager verification invalidate the pivot.

If eager observes a failing validator that pivot skipped, verdict is:

```text
unsafe_skip_observed
```

Speed does not rescue that run.

### Docs

- `FOUNDING.md` — conceptual boundaries.
- `WORK_STATE.md` — unfinished work vs delayed messages and baseline guardrails.
- `GATE_A_REAL_REENTRY.md` — actual timing protocol and kill criteria.
- this file — current frontier.

### Tests / CI
Known-answer tests cover delay, modulation, baseline policy, work lifecycle, local visibility, async completion order, worker failure, and cancellation.

Toy/unit-test success is not architecture evidence.

---

## What NOT to claim

- This is not a model of free will.
- This is not a biological model of dopamine, serotonin, hormones, dendrites, or neurotransmission.
- This is not evidence that memories are consciously steered through hippocampal waves.
- This is not a new asynchronous scheduler.
- This is not a new value-of-information algorithm.
- A transformer can be a worker inside PivotPoint.
- An ordinary transformer-agent given the same compact live-state snapshot is a mandatory future baseline.
- Similarity to brains earns no score by itself.

---

## The most important inherited failures

### PerceptionLab
Persistent state alone was not temporally interesting. The calibrated wave-field demo showed the useful primitive cleanly: a single current state can contain consequences at different causal ages when real propagation/ringdown exists. Treat it as an instrument/demo result, not brain evidence.

### KYY
Generic temporal ordering/locality stories failed strong controls. Monotone temporal blocks did not beat matched non-monotone contiguous blocks; residual advantage belonged largely to spatial contiguity. KYY also established the methodological rule: geometry must beat strong algebraic/structured baselines, not merely solve the task.

Carry that rule here:

> PivotPoint must beat ordinary schedulers, dependency graphs, compact snapshots, and strong sequential-decision baselines when they receive the same information and budget.

### WidePresent
Completed transcript can alias distinct live worlds. The important difference may be unfinished work: “nothing requested” versus “refresh already in flight.” That observation motivated `WorkRegistry`.

### PresentMoment
The useful surviving brain-side object was receiver/state-dependent accessibility, but repeated estimator/control failures killed several prettier stories. Do not use neuroscience citations as evidence for PivotPoint.

### FunctionalArbors
A particularly relevant failure: credit transport could work while free structural credit assignment still failed. Recent activity or exact branch identity was not sufficient to identify which structural event caused the later useful outcome.

Therefore structural growth in PivotPoint must **not** use “active near later success” as credit. If growth is reopened, prefer a measured intervention mark such as change in reachable/readable state before vs after the structural event, with matched controls/counterfactual approximations.

Do not implement growth yet.

---

## The live architecture hypothesis

Do not begin with a monolithic latent vector.

```text
specialized local workers
        │
        ├── delayed signals whose payload already exists
        │
        ├── unfinished WorkItems whose result is not born yet
        │
        ├── local inboxes / local work visibility
        │
        ├── fixed possible wiring
        │       +
        │   dynamic effectome
        │
        ├── slow modulators with heterogeneous receptor profiles
        │
        └── local action offers
                   │
                   ▼
              SMALL PIVOT POLICY
                   │
        choose probe / route / wait /
        inhibit / amplify / execute / cancel
                   │
                   ▼
         altered future accessibility
```

High-capacity semantic processing can be delegated to workers. The controller should remain small until data forces otherwise.

---

## Immediate experiments — current order

### Gate A — run real re-entry receipts now

The harness exists. Stop coding around it until some realistic repositories have receipts.

Example:

```bash
python examples/benchmark_git_reentry.py \
    --repo . \
    --test "python -m pytest -q" \
    --docs-test "python -m mkdocs build --strict" \
    --repeats 5 \
    --json gate_a.json
```

Run on realistic interrupted/dirty trees, not clean checkouts.

**Kill/downgrade if:** unsafe eager-only failures appear, savings are small, classifier/schema maintenance dominates, or a compact verified snapshot/build dependency graph is cheaper and safer.

### Gate B — asynchronous held-out environment

Now that unfinished work is a real runtime object, build the comparison.

Required baselines:

1. ordinary event loop / priority queue;
2. global barrier / wait-for-all where appropriate;
3. compact full live-state snapshot;
4. sequential value-of-information / optimal-stopping style baseline for tasks where that formulation applies;
5. transformer-agent baseline later if the same task reasonably admits one.

Do **not** hand-author worlds where acting locally is guaranteed to win. Use externally generated/held-out tasks or real variable-latency workers.

Score at minimum:

- task success/utility;
- wall-clock/deadline misses;
- compute/work launched;
- cancelled/wasted work;
- amount of live state exposed to the controller;
- policy/schema complexity.

**Kill:** if an ordinary scheduler/behavior tree/compact global snapshot matches PivotPoint with less machinery.

### Gate C — dynamic effectome

Only after Gate B has a fair harness.

Fixed wiring, changing task regimes. Compare:

- no modulation;
- one global scalar;
- multiple modulators with identical receptor profiles;
- heterogeneous receptor profiles.

**Kill:** if heterogeneous modulation adds no held-out adaptation benefit relative to simpler routing/adaptation methods.

### Structural growth — still locked

Only reopen if A/B/C earn it.

If reopened, use measured causal change in accessibility/control rather than activity/reward proximity as eligibility.

---

## Mouse task branch (do not accidentally restart here)

The PresentMoment mouse spiral/task audit remains a separate branch.

Last known state:

- remote extraction of the designated held-out task files for `ZYE_0085` and `ZYE_0091` completed;
- initial two-mouse past-only models did not beat simple stimulus/side baselines;
- the authors' nominal pre-stimulus phase analysis had a timing/acausal-filtering problem;
- resume the frozen held-out analysis in **PresentMoment**, not PivotPoint, unless its result becomes a direct benchmark here.

---

## Process rule

When the idea becomes smooth enough that every result is predictable, stop theorizing and find a system with permission to say **no**.

Failures belong in this repository.
