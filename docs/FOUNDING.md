# Founding note — from a wide present to a pivot point

This repository was opened after a long sequence of experiments about temporal state, causal age, asynchronous processing, distributed waves, memory re-entry, and agent interruption.

Most of those branches became more useful when their grand language was removed.

The surviving question is small:

> **What can a system do from its current local state that changes what it will be able to read next?**

That is the PivotPoint.

---

## 1. The small present

The earlier framing asked how *wide* the present might be.

The newer framing asks where a real system can still **branch**.

A local unit does not possess the whole organism or agent. It has only a constrained present:

```text
local readable state
signals already arrived
signals still in flight (usually not directly visible)
slow context / modulators
currently effective routes
a finite action set
resource / timing constraints
```

From that small state, some interventions are possible and others are not.

A useful present is therefore less like a rectangular time window and more like a **causal branching surface**.

---

## 2. Nominal actions are not effective actions

An important distinction:

```text
NOMINAL OPTION
    an action can be represented, named or imagined

EFFECTIVE OPTION
    the current system can actually recruit enough of the required downstream
    path for the action to materially change future state/accessibility
```

A person may be able to think “I should go for a bike ride” while being in a bodily/affective state in which that thought has little control authority. In another state the same thought may rapidly recruit action.

This document does **not** claim a mechanism for depression, stress, motivation or free will. The example is used only to make an engineering distinction sharp:

> **Representability of an action is not the same as controllability of the action.**

For artificial systems this is immediately testable. A planner may emit an action token that the current tool graph, permissions, resource budget, pending work, or dynamic gates cannot presently execute.

---

## 3. A practical degree of freedom

PivotPoint avoids defining metaphysical free will.

It does define a local **control degree of freedom**.

Let the feasible actions at time `t` be `A_t`. For each action, consider the future accessibility pattern it can produce:

```text
R_t(a) = what becomes readable/reachable after taking action a
```

If two actions produce effectively the same `R_t`, they are not two meaningful control degrees of freedom merely because they have different names.

The useful branching factor is therefore the number/dimension of *materially distinguishable reachable futures*.

This suggests several measurable quantities:

- number of feasible actions;
- number of equivalence classes under similar reachable consequences;
- entropy of reachable futures under the current policy;
- rank/effective rank of action-to-readout influence;
- controllability under a cost or deadline budget.

The important phrase is **under the current state**. Modulation can change these values without changing the static wiring.

---

## 4. Wiring versus effectome

A static graph describes possible influence.

A living/running system requires another object:

```text
connectome / wiring     potential routes

effectome               effective influence now
```

An edge may be structurally present but functionally weak, gated, saturated, refractory, occupied, mismatched to the receiver, or irrelevant to the current population pattern.

PivotPoint therefore treats edge efficacy as state-dependent.

This gives a direct engineering target:

```text
static graph
    +
slow modulators
    +
receiver state
    +
route state
    =
dynamic effective graph
```

The dynamic graph determines which nominal actions are actually effective.

---

## 5. Chemistry-inspired modulation without cartoon neurotransmitters

The nervous system does not communicate only through identical pulses on fixed wires. Chemical and modulatory systems alter operating regimes across many spatial and temporal scales.

PivotPoint keeps only the abstract engineering lesson for now:

> **Some signals should change how other signals are processed rather than carry the task content themselves.**

A modulator may change:

- edge gain;
- firing/action threshold;
- persistence or decay;
- exploration/exploitation balance;
- plasticity rate;
- effective action cost;
- routing preference;
- cooldown/refractory behavior.

Different nodes and edges have different receptor profiles, so the same modulator produces heterogeneous local effects.

This may be far more expressive than a single global scalar such as “temperature” or “reward.”

It is still ordinary engineering until external tasks show that it buys something.

---

## 6. Re-entry as active query

A recurring subjective observation motivated this branch:

When a memory cannot be recalled directly, one strategy is to **re-enact a sequence**:

```text
I was here
then I opened this
then I thought about that
then I moved to...

oh — there it is
```

The strong hypothesis is not that conscious thought directly drives a known hippocampal loop.

The useful computational interpretation is simpler:

> **An action sequence can function as a query by moving the system through internal states until a previously inaccessible trace becomes readable.**

That differs from querying a static memory database with a better text key.

In schematic form:

```text
trace/state M may already exist

current readout state z0 cannot expose it
        │
      action
        ▼
       z1
        │
      action
        ▼
       z2
        │
      action
        ▼
       z3  -> M becomes readable
```

This is **active re-entry**.

A second strategy is **rendezvous/waiting**: avoid perturbing the system and allow an endogenous process already in flight to arrive at a readable state.

PivotPoint should eventually support both.

---

## 7. Structural growth: the dendrite-like question

A future direction is to let the architecture grow routes rather than fixing every path by hand.

The weak version would be decorative: “grow a branch when activity is high.”

The stronger engineering question is:

> **Can repeated unresolved pivots identify where a new local route would create a genuinely new reachable future?**

Possible rule:

```text
repeated state family
    +
important desired readout remains inaccessible
    +
there exists a recurrent useful intermediate
    +
new route reduces cost / delay / failure on held-out episodes
        ->
consider structural branch
```

The route survives only if it continues to earn its cost.

This is inspired by biological structural plasticity only at the level of “structure can change with experience.” It is not a proposed dendritic growth mechanism.

---

## 8. What makes this different from a transformer?

The intended contrast is architectural, not mystical.

A standard transformer forward pass receives an assembled context and transforms it through a fixed sequence of layers. Agent frameworks can wrap transformers in memory, tools and asynchronous control, but those properties are **outside the transformer block itself**.

PivotPoint makes the following first-class runtime state:

- incomplete/in-flight work;
- receiver-local readout;
- dynamic route efficacy;
- slow modulators;
- action-conditioned future accessibility;
- structural changes to the route graph.

A transformer can be inserted as a high-capacity semantic worker. The experiment is whether the overall system can avoid requiring the transformer to be the global clock, global memory, global planner and global state integrator all at once.

---

## 9. The first three gates

### Gate A — real task re-entry

Use real repositories and real command timings.

Compare:

```text
full verified snapshot
versus
small local pivot -> conditional expensive probes
```

Score correctness, wall-clock, compute, and maintenance burden.

If savings are trivial after schema/maintenance cost, kill the product branch.

### Gate B — asynchronous tool environment

Create tasks in which several workers/tools have different latencies and results become available at different times.

Compare a monolithic “wait and rebuild global state” controller with a PivotPoint controller that can act locally while work remains in flight.

The environment must be externally generated or held out; do not hand-author worlds that guarantee the desired result.

### Gate C — dynamic effectome

Keep wiring fixed while changing task regimes.

Test whether multi-timescale modulators with heterogeneous receptor profiles let the same network adapt with less retraining/replanning than static routing.

Ablations:

- no modulators;
- one global modulator;
- multiple modulators but identical receptor profiles;
- heterogeneous receptor profiles.

If heterogeneous modulation does not improve adaptation on held-out regime changes, do not keep it because it sounds biological.

---

## 10. Stop conditions

PivotPoint should stop expanding if it becomes another vocabulary machine.

Warning signs:

- every new result is mathematically guaranteed by the metric;
- every failure produces a renamed concept rather than a closed branch;
- brain papers are used only because they resemble the architecture;
- no external benchmark is allowed to say “no”;
- the system becomes an elaborate scheduler that does not outperform a simple scheduler;
- a transformer baseline matches it with less machinery.

The repo earns complexity only from contact.
