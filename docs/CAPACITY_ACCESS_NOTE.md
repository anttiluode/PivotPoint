# Capacity versus access

A useful external boundary arrived from Aizenbud et al. 2026, *What can a neuron compute?* (`10.64898/2026.06.08.730984`). Their TwinProp method uses a digital twin and gradients to optimize synaptic strengths and dendritic locations in a detailed rat L5 pyramidal-cell model. The resulting cell can solve strongly nonlinear tasks, while simplifications of dendritic nonlinear mechanisms substantially reduce performance.

For PivotPoint, this suggests a clean separation:

```text
CAPACITY
what the large substrate is capable of computing

ACCESS
which capability becomes useful from the current local state
```

PivotPoint should focus on the second object. A small controller does not need to contain or recreate the high-dimensional computation. It may only need to choose a query, route, wait, gate or worker that makes an already-learned capability consequential next.

This also preserves the lesson from RegionalAttractorExplorer Gate Q: a small timing/state change can alter the distributed response without increasing its dimensionality. Control may select or reweight existing trajectories rather than create more dimensions.

Therefore future PivotPoint metrics should reward useful changes in the **identity, cost or accessibility of reachable futures**, not raw activity variance or rank by themselves.

A strong baseline remains a direct call to the powerful worker. If a small pivot layer does not save latency, compute, interference or relearning relative to that baseline, it has earned nothing.
