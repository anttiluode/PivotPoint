# PivotPoint

**A small actionable present for asynchronous intelligence.**

> **CONTROL:** what can I do **now** that changes what I will be able to read **next**?

PivotPoint starts from a different primitive than a context window, a global snapshot, or a wider representation of the present.

A **pivot point** is a *local causal branching surface*: a moment at which a system has only partial local state, some processes still in flight, a constrained set of actions, and the ability to choose an action that changes what becomes accessible later.

The intended architecture is deliberately not “a tiny transformer.” A transformer may eventually be one useful specialist inside it, but it is not the organizing principle.

## The core object

At time `t`, a pivot sees only a small local view:

```text
                   signals already readable
                            │
                            ▼
                    ┌────────────────┐
     slow state ───►│   PIVOT POINT  │◄── local wiring / gates
   / modulators     └───────┬────────┘
                            │
                   currently possible actions
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
          probe           route            wait
            │               │               │
            └───────────────┼───────────────┘
                            ▼
                different future readouts
```

The important state is not merely “what is stored.” It is also:

- what is readable **here**;
- what signals and computations are still **in flight**;
- what actions are presently **feasible**;
- which routes are currently effective rather than merely wired;
- what those actions are expected to make readable later.

This gives a compact operational decomposition:

```text
current state
+ causal maturity
+ receiver-relative accessibility
+ reachable accessibility
```

`reachable accessibility` is the new term that matters here: **what could become readable next, given the actions and internal trajectories available from this local state?**

## Why “small,” not “wide”

A biological neuron does not receive “the brain.” It receives a brutally local condition: particular synapses, dendrites, membrane state, ion-channel state, modulators, field conditions, arriving signals and body-state influences.

Likewise, a PivotPoint should not require a complete synchronized reconstruction of the whole agent before acting. Intelligence should be able to arise from many small local pivots embedded in an asynchronous system.

The working hypothesis is therefore not “the present has width.” It is:

> **The useful present is where constrained local state meets a set of materially different reachable futures.**

## Wiring is not the effectome

A connection only means that influence is *possible*. It does not guarantee that the current state can traverse that connection or affect the receiver.

PivotPoint therefore separates:

```text
WIRING        who can potentially talk to whom
EFFECTOME     who can affect whom right now, and how strongly
```

The effectome can vary because of:

- gates;
- slow modulators;
- local thresholds;
- receiver state;
- route occupancy;
- refractory / cooldown state;
- learned gain changes;
- resource or energy limits.

This distinction is central. A memory or signal may exist without being readable. A route may exist without currently carrying the relevant projection.

## Modulation: the chemistry-inspired layer

The first implementation treats “chemistry” only as an engineering abstraction, **not as a claim that artificial modulators reproduce neurotransmitters or hormones**.

A modulator does not need to carry semantic content. It can instead change the operating regime of many edges or nodes on a slower timescale:

```text
urgency       -> lower some action thresholds
fatigue       -> increase expensive-action costs
novelty       -> increase exploratory gain
stability     -> lengthen persistence / reduce switching
stress-like   -> alter which routes dominate
```

Different edges/nodes can have different **receptor profiles**, so the same global modulator affects different local circuits differently. This creates a dynamic effectome without rewriting the wiring graph every step.

## Control without metaphysics

PivotPoint does not define philosophical free will.

It does define an experimentally useful **control capacity**.

Let `A_t` be the currently feasible actions. Two nominally different actions do not count as two useful degrees of freedom if they lead to effectively the same future accessibility. The interesting quantity is the number/dimension of *materially distinct reachable readout states* opened by the available actions.

So a future metric may look like:

```text
nominal actions             12
materially distinct futures  3
control degrees of freedom   ~3, not 12
```

This makes “degree of freedom” testable rather than rhetorical.

## What this is trying to build

The first target is a runtime with:

1. **specialized workers** rather than one monolithic cognition block;
2. **signals in flight** with delay, age, expiry and destination;
3. **local readouts** rather than one omniscient state vector;
4. a dynamic **effectome** layered on fixed wiring;
5. **slow modulators** with worker/edge-specific receptor profiles;
6. **offers**: local candidate actions with cost and expected unlocks;
7. a small **pivot policy** that chooses what to probe, route, wait for, inhibit, amplify or execute;
8. structural growth later: add routes/branches when repeated experience shows that a new local path materially improves future accessibility.

That final item is the dendrite-like direction worth exploring: **do not grow structure because a hand-written rule says “branch here”; grow it where repeated unresolved pivots reveal a useful new route.** This is an engineering analogy, not a biological mechanism claim.

## First practical contact

The first practical demo is intentionally mundane: **task re-entry after interruption**.

An interrupted agent should not always rebuild a maximal snapshot. Some facts are already recorded and cheap to read; others only exist after an expensive measurement (tests, simulation, render, network query, model call).

A PivotPoint can inspect cheap local state first and only create expensive measurements when their outcome can still change the next action.

That gives us a real falsifiable gate:

> On real projects, does the pivot policy reduce wall-clock/compute cost while preserving correct re-entry decisions?

If not, that branch dies.

## Scientific / engineering guardrails

- A toy whose result is forced by its definition is a **unit test**, not evidence.
- A brain analogy earns nothing unless it generates a measurement that could disagree.
- “Looks wave-like,” “looks dendritic,” or “resembles neuromodulation” is not validation.
- Transformer baselines remain mandatory wherever a transformer can reasonably solve the same task.
- Prefer external datasets, real command timings and held-out environments over self-authored arithmetic.
- Preserve nulls and failed branches in the repo.

## Repository map

```text
pivotpoint/
    core.py          minimal asynchronous/effectome primitives
examples/
    git_reentry.py   first real-world pivot demo
docs/
    FOUNDING.md      conceptual boundary and research questions
    HANDOFF.md       state for the next model/session
```

## Immediate build order

1. Make the core runtime tiny and inspectable.
2. Run `git_reentry.py` on real repositories and record actual timings.
3. Add asynchronous workers and delayed signals.
4. Add modulators/receptor profiles and test whether they improve adaptation across changing task regimes.
5. Only then attempt a larger non-transformer cognitive benchmark.

The repo should remain small until reality forces it to grow.
