# HANDOFF — read this first on reboot

## One-sentence state

**PivotPoint is an attempt to build intelligence around a small local causal branching surface: choose an action now that changes what will become readable next.**

Do not restart from “how wide is the present?”

---

## Why this repo exists

The preceding work repeatedly converged on four distinct questions:

1. does a trace/state exist?
2. is it readable by this receiver now?
3. can an available action/trajectory make it readable next?
4. if readable, does it actually control behavior?

The new repo isolates #3 while retaining #1/#2/#4 as constraints.

The key move is from **memory as stored content** to **re-entry as control of future observability**.

---

## Core vocabulary — do not rename unless data forces it

### PivotPoint
A local state where materially different future readouts are reachable through currently feasible actions.

### Nominal option
An action that can be represented/named.

### Effective option
An action whose required downstream route is currently open enough to materially alter future state/accessibility.

### Wiring
Potential communication graph.

### Effectome
Current effective influence graph after gates, modulators, receiver state, occupancy, resource constraints, etc.

### Modulator
A slower control signal that changes gains/thresholds/persistence/routing/plasticity rather than carrying task content itself.

### Reachable accessibility
What can become readable next under actions/trajectories available from the current local state.

### Control degrees of freedom
The effective number/dimension of materially different reachable futures, not the raw count of named actions.

---

## What NOT to claim

- This is not a model of free will.
- This is not a biological model of dopamine, serotonin, hormones, dendrites, or neurotransmission.
- This is not evidence that memories are retrieved by consciously steering hippocampal waves.
- This is not a claim that transformers cannot be agents; wrappers can add tools, memory, scheduling and asynchronous state.
- A transformer may be a worker inside PivotPoint.
- Similarity to brains earns no score by itself.

---

## What already exists in this repo

- `README.md` — architecture and first falsifiable product gate.
- `docs/FOUNDING.md` — conceptual boundaries, effective-vs-nominal options, control DOF, modulation and structural growth.
- `pivotpoint/core.py` — minimal signals-in-flight + dynamic-effectome substrate + transparent action-offer policy.

Immediate coding target: keep the runtime dependency-free and small enough to inspect in one screenful/short file.

---

## Related work that should NOT be rediscovered from scratch

### PerceptionLab
The old checkerboard accident led to a calibrated wave-field demo. A local impulse propagated past separated probes with the expected lag. Useful lesson: persistent state alone is not “temporal thickness”; distinguishable causal ages require propagation/ringdown/different unfinished processes. Treat this as an instrument/demo result, not brain evidence.

### KYY
Generic temporal ordering/locality stories were attacked. Monotone temporal ordering did not beat matched non-monotone contiguous blocks; residual advantage belonged largely to spatial contiguity. Do not resurrect “order itself is fundamental.”

### WidePresent
A practical re-entry branch emerged: recorded state is cheap; measured state may require expensive tests/renders/network/model calls. Conditional probing may save cost over eager verified snapshots. The real test is wall-clock on real repos, not assigned toy costs.

### PresentMoment — mouse spiral/task audit
Last-night state before this repo opened:

- Authors' task dataset is one ~14.21 GiB `task.zip`, but remote ZIP range reads can access individual members without downloading the archive.
- The archive contains 1,157 members; small/processed task members were successfully extracted with `remotezip` in GitHub Actions.
- Authors' behavioral plotting code uses four mice but computes one plotted SEM with `sqrt(6)`; visual error bars are therefore too small in that plot.
- More importantly, their so-called pre-stimulus 2–8 Hz phase analysis samples the trial-alignment frame at/just after photodiode onset and the phase was generated with offline `filtfilt` + Hilbert processing. Therefore that code does **not cleanly establish** that genuinely pre-evidence state predicts detection.
- A frozen past-only check was started using raw fluorescence from roughly -1.0 to -0.2 s, avoiding post-stimulus samples and avoiding the acausal phase variable.
- On the two initially available mice (`ZYE_0088`, `ZYE_0090`), a simple stimulus/side baseline beat models augmented with local or six-site neural history on held-out log loss. This was a negative preliminary contact, not a final cohort result.
- `ZYE_0085` and `ZYE_0091` were designated subject holdouts under the frozen specification and extraction was launched.

Resume that work in **PresentMoment**, not here, unless its result directly becomes a PivotPoint benchmark.

---

## The live architecture hypothesis

Do not begin with a monolithic latent vector.

Begin with:

```text
specialized local workers
        │
        ├── delayed / in-flight signals
        │
        ├── local inboxes
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
              PIVOT POLICY
                   │
        choose probe / route / wait /
        inhibit / amplify / execute
                   │
                   ▼
         altered future accessibility
```

The pivot policy should remain tiny initially. High-capacity semantic processing can be delegated to workers.

---

## Immediate experiments, in order

### 1. Real git/task re-entry
Build a CLI that reads cheap recorded facts and conditionally launches expensive measurements. Record real wall-clock and compare against eager verification. Include maintenance/schema cost in the discussion.

**Kill:** if savings are small or task-specific logic dominates.

### 2. Async held-out environment
Use tasks with real variable-latency workers. Compare PivotPoint to a simple event loop/scheduler and to a transformer-agent baseline.

**Kill:** if an ordinary priority queue / behavior tree matches it with less machinery.

### 3. Dynamic-effectome gate
Fixed wiring, changing task regimes. Compare no modulation / one scalar / homogeneous receptors / heterogeneous receptors.

**Kill:** if the receptor/modulation layer adds no held-out adaptation benefit.

### 4. Structural growth only after 1–3
Test whether repeated unresolved pivots identify useful new routes. New branches must pay rent in held-out task cost, latency or success.

---

## Process rule

When the idea becomes smooth enough that every result is predictable, stop theorizing and find an external system with permission to say **no**.

Failures belong in this repository.
