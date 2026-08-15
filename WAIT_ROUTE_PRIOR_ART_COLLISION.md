# WAIT versus ROUTE — prior-art collision

**Date:** 2026-08-15  
**Status:** the abstract decision problem is strongly occupied. **Do not claim WAIT/ROUTE active sensing as novel.**

## Why this note exists

A cross-project Dig experiment on one fixed dendritic medium produced a clean systems distinction:

```text
WAIT
    retain the same readout C
    increase observation horizon T
    accumulate more discrimination evidence

ROUTE
    change readout C
    change which evidence is observed
    potentially change the asymptotic discrimination ceiling
```

That maps naturally onto PivotPoint's existing question:

```text
what can I do now that changes what I will be able to read next?
```

But the abstract decision problem is not new.

---

# Closest occupied literature

## Naghshvar & Javidi — Active Sequential Hypothesis Testing

Mohammad Naghshvar and Tara Javidi, *The Annals of Statistics* 41(6), 2013, pp. 2703-2738.

Preprint:

https://arxiv.org/abs/1203.4626

This line explicitly studies a decision maker that:

```text
sequentially collects observations
adaptively chooses the next sensing action
trades information acquisition speed against decision error / cost
and decides when to stop
```

That already occupies the conceptual territory:

```text
continue observing under current policy
vs
choose a more informative sensing action
vs
stop and decide.
```

The paper derives information-acquisition bounds and asymptotically optimal active sensing policies.

## Nitinawarat, Atia & Veeravalli — Controlled Sensing for Multihypothesis Testing

Sirin Nitinawarat, George K. Atia, Venugopal V. Veeravalli, *IEEE Transactions on Automatic Control* 58(10), 2013, 2451-2464.

DOI:

https://doi.org/10.1109/TAC.2013.2261188

Preprint:

https://arxiv.org/abs/1205.0858

This studies multiple-hypothesis testing where observation/control actions determine the quality/distribution of the data collected, in both fixed-sample and sequential settings.

Again, adaptive sensing + stopping is already the object.

## Li et al. — Sequential Hypothesis Test with Online Usage-Constrained Sensor Selection

Shang Li, Xiaoou Li, Xiaodong Wang, Jingchen Liu, *IEEE Transactions on Information Theory* 65(7), 2019, 4392-4410.

DOI:

https://doi.org/10.1109/TIT.2019.2910730

Preprint:

https://arxiv.org/abs/1601.06447

This is especially close to the naive `WAIT` / `ROUTE` story:

```text
select one most-informative sensor online from past observations
continue sampling until a reliable decision can be made
include sensor usage costs / constraints
formulate the problem through Bayesian optimal stopping
```

So sensor switching / sensing cost / stopping is emphatically occupied.

## Broader POMDP active information gathering

Modern POMDP work also explicitly treats actions whose purpose is to reveal information needed for a later task. One example is:

Annie Xie et al., *Learning to Explore in POMDPs with Informational Rewards*, ICML 2024.

https://proceedings.mlr.press/v235/xie24a.html

This is broader than the sequential-testing literature but reinforces the same boundary: information-gathering actions are a standard partially-observed planning object.

---

# What Dig actually contributed to this repo

Nothing above is a novelty claim.

Dig supplied one measured toy instantiation of the generic variables.

On the fixed Hay `cell1.asc` source-response tensor it measured:

```text
D_C,T^2(i,j)
    = integral_0^T || h_i(t) - h_j(t) ||^2 dt
```

and verified that it is monotone in `T` for every tested source pair / readout.

Under 128 fixed random readouts per retained output dimension `k`, median pairwise discrimination energy at 120 ms saturated at approximately:

```text
k=1     12.8% of full six-port reference
k=2     29.7%
k=3     45.9%
k=4     64.4%
k=5     88.7%
k=6    100.0%
```

So in that medium:

```text
more WAIT cannot compensate for every readout bottleneck.
```

This is ordinary finite-horizon observability / controlled-sensing behavior, but it gives PivotPoint a concrete internal example instead of a metaphor.

---

# The clean PivotPoint taxonomy

Use the systems roles carefully:

```text
WAIT
    keep readout / sensing action fixed
    gather more evidence over time

ROUTE
    change observation/readout channel

PROBE
    deliberately inject an input whose consequence may separate hypotheses

ACT
    alter the controlled world/state for task reasons

MODULATE / GATE
    alter internal dynamics / effective propagation

DECIDE / STOP
    terminate information acquisition and commit to an action/hypothesis
```

The categories can overlap in real systems, but they should not all be called `geometry deformation`.

---

# Where PivotPoint can still have a project-specific question

The novelty cannot be:

```text
agents should sometimes gather information before acting
agents should choose informative sensors
agents should decide when to stop waiting
```

Those are old and deep fields.

The remaining project-specific intersection, if worth testing, is narrower:

```text
late / out-of-order evidence
+ source-specific validity frontiers
+ asynchronous tool / worker results
+ explicit world-time vs knowledge-time bookkeeping
+ actions with different future-readout consequences
```

In other words:

> **Does WidePresent-style exact temporal provenance make an ordinary active-sensing / stopping decision easier or safer in asynchronous agent loops?**

That is an engineering benchmark question, not a new decision-theory claim.

A good benchmark would force the agent to distinguish cases such as:

```text
WAIT:
    current channel can become sufficient before deadline

ROUTE:
    current channel has saturated / cannot meet required reliability,
    another available channel can

PROBE:
    no passive readout resolves the remaining hypotheses efficiently,
    but an intervention will

ACT NOW:
    deadline / action cost makes further sensing worse than committing
```

and then add the specifically WidePresent complication:

```text
some observations describe old world states but are newly known
some results are still in flight
some cached results are stale under source-specific validity rules
some predictions concern future world time
```

That intersection is much less obviously identical to the classical examples, but it still needs a precise prior-art collision before any novelty language.

---

# Baseline / stop condition

Before training or changing an LLM architecture:

1. Build the smallest synthetic decision table.
2. Write an exact deterministic resolver from the known generative rules.
3. Verify the resolver reaches 1.0.
4. Give the LLM the raw case, then optional temporal/readout side information.
5. If the deterministic resolver is enough for the intended product, **use it and stop**.
6. If an LLM with ordinary tool use already infers the correct action, do not add PivotPoint machinery.

## One-line handoff

> **WAIT/ROUTE/PROBE/STOP is active sequential sensing, not a new primitive. PivotPoint's remaining question is whether explicit asynchronous temporal provenance and source-specific validity change those already-known decisions in a way that ordinary agents fail to handle.**
