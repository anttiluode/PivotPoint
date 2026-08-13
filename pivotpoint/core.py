"""Minimal primitives for PivotPoint.

This file is intentionally small.  It is not a brain model.

It provides four engineering objects that the repo needs before any larger
architecture is justified:

1. signals that can remain *in flight*;
2. fixed wiring whose momentary efficacy can be modulated (an effectome);
3. local inboxes rather than a globally synchronized state vector;
4. action offers describing how a local intervention may change future access.

No transformer, neural-network framework, or third-party dependency is required.
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
import heapq
import math
from typing import Any, Deque, Dict, Iterable, List, Mapping, Optional, Tuple


@dataclass
class ModulatorState:
    """Slow global/context state.

    Names are deliberately domain-neutral.  A caller may use labels such as
    ``urgency`` or ``fatigue``, but these are engineering control variables,
    not claims about particular neurotransmitters or hormones.
    """

    values: Dict[str, float] = field(default_factory=dict)

    def get(self, name: str, default: float = 0.0) -> float:
        return float(self.values.get(name, default))

    def set(self, name: str, value: float) -> None:
        self.values[name] = float(value)

    def update_toward(self, targets: Mapping[str, float], rate: float = 0.1) -> None:
        """Relax modulators toward targets on a slower timescale."""
        rate = max(0.0, min(1.0, float(rate)))
        for name, target in targets.items():
            old = self.get(name)
            self.values[name] = old + rate * (float(target) - old)


@dataclass(frozen=True)
class Edge:
    """Potential connection between two local nodes.

    ``receptors`` describes how slow modulators change the *efficacy* of this
    already-existing edge.  Wiring therefore remains separate from the
    momentary effectome.
    """

    source: str
    target: str
    delay: float = 0.0
    base_gain: float = 1.0
    receptors: Mapping[str, float] = field(default_factory=dict)
    enabled: bool = True

    def effective_gain(self, modulators: ModulatorState) -> float:
        if not self.enabled:
            return 0.0

        # Multiplicative modulation keeps gain positive while allowing several
        # slow factors to combine.  Clamp exponent to avoid accidental overflow.
        drive = sum(float(weight) * modulators.get(name)
                    for name, weight in self.receptors.items())
        drive = max(-8.0, min(8.0, drive))
        return float(self.base_gain) * math.exp(drive)


@dataclass
class Signal:
    source: str
    target: str
    payload: Any
    kind: str = "signal"
    strength: float = 1.0
    created_at: float = 0.0
    available_at: float = 0.0
    expires_at: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def age_when_available(self) -> float:
        return float(self.available_at - self.created_at)


@dataclass(frozen=True)
class ActionOffer:
    """A locally proposed intervention at a pivot.

    The runtime does not pretend to know the correct utility model.  It merely
    makes explicit the quantities that later experiments must estimate rather
    than hide inside prose.
    """

    owner: str
    action: str
    expected_value: float = 0.0
    expected_accessibility_gain: float = 0.0
    cost: float = 0.0
    risk: float = 0.0
    unlocks: Tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PivotDecision:
    offer: ActionOffer
    score: float
    reasons: Mapping[str, float]


class PivotPolicy:
    """Transparent baseline policy.

    This is deliberately *not* presented as a cognitive theory.  It exists so
    later policies have a boring, inspectable baseline to beat.
    """

    def __init__(
        self,
        value_weight: float = 1.0,
        accessibility_weight: float = 1.0,
        cost_weight: float = 1.0,
        risk_weight: float = 1.0,
    ) -> None:
        self.value_weight = float(value_weight)
        self.accessibility_weight = float(accessibility_weight)
        self.cost_weight = float(cost_weight)
        self.risk_weight = float(risk_weight)

    def choose(
        self,
        offers: Iterable[ActionOffer],
        modulators: Optional[ModulatorState] = None,
    ) -> Optional[PivotDecision]:
        modulators = modulators or ModulatorState()

        # Generic slow controls.  They are optional and intentionally simple.
        urgency = modulators.get("urgency")
        conservation = modulators.get("conservation")
        caution = modulators.get("caution")

        best: Optional[PivotDecision] = None
        for offer in offers:
            value_term = self.value_weight * offer.expected_value * (1.0 + urgency)
            access_term = (
                self.accessibility_weight * offer.expected_accessibility_gain
            )
            cost_term = self.cost_weight * offer.cost * math.exp(conservation)
            risk_term = self.risk_weight * offer.risk * math.exp(caution)
            score = value_term + access_term - cost_term - risk_term

            decision = PivotDecision(
                offer=offer,
                score=float(score),
                reasons={
                    "value": float(value_term),
                    "accessibility": float(access_term),
                    "cost": float(-cost_term),
                    "risk": float(-risk_term),
                },
            )
            if best is None or decision.score > best.score:
                best = decision

        return best


class PivotRuntime:
    """Tiny asynchronous signal substrate with local inboxes.

    There is one objective runtime clock, but nodes do not receive a global
    snapshot.  They only receive signals whose route has completed.
    """

    def __init__(self) -> None:
        self.now: float = 0.0
        self.modulators = ModulatorState()
        self._edges: Dict[str, List[Edge]] = defaultdict(list)
        self._inboxes: Dict[str, Deque[Signal]] = defaultdict(deque)
        self._queue: List[Tuple[float, int, Signal]] = []
        self._counter: int = 0
        self.history: List[Signal] = []

    def connect(self, edge: Edge) -> None:
        self._edges[edge.source].append(edge)

    def outgoing(self, source: str) -> Tuple[Edge, ...]:
        return tuple(self._edges.get(source, ()))

    def emit(
        self,
        source: str,
        payload: Any,
        *,
        kind: str = "signal",
        strength: float = 1.0,
        ttl: Optional[float] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> List[Signal]:
        """Send a local emission along currently effective outgoing routes."""
        scheduled: List[Signal] = []
        for edge in self._edges.get(source, ()):
            gain = edge.effective_gain(self.modulators)
            if gain == 0.0:
                continue

            available = self.now + max(0.0, float(edge.delay))
            expires = None if ttl is None else self.now + max(0.0, float(ttl))
            signal = Signal(
                source=source,
                target=edge.target,
                payload=payload,
                kind=kind,
                strength=float(strength) * gain,
                created_at=self.now,
                available_at=available,
                expires_at=expires,
                metadata=dict(metadata or {}),
            )
            self._counter += 1
            heapq.heappush(self._queue, (available, self._counter, signal))
            scheduled.append(signal)
        return scheduled

    def advance(self, dt: float) -> List[Signal]:
        """Advance time and deliver every signal whose route has completed."""
        if dt < 0:
            raise ValueError("PivotRuntime cannot run backward")
        self.now += float(dt)

        delivered: List[Signal] = []
        while self._queue and self._queue[0][0] <= self.now:
            _, _, signal = heapq.heappop(self._queue)
            if signal.expires_at is not None and self.now > signal.expires_at:
                continue
            self._inboxes[signal.target].append(signal)
            self.history.append(signal)
            delivered.append(signal)
        return delivered

    def read(self, node: str, *, kind: Optional[str] = None) -> List[Signal]:
        """Consume currently readable local signals for ``node``."""
        inbox = self._inboxes[node]
        kept: Deque[Signal] = deque()
        selected: List[Signal] = []

        while inbox:
            signal = inbox.popleft()
            if signal.expires_at is not None and self.now > signal.expires_at:
                continue
            if kind is None or signal.kind == kind:
                selected.append(signal)
            else:
                kept.append(signal)

        self._inboxes[node] = kept
        return selected

    def pending(self, *, target: Optional[str] = None) -> List[Signal]:
        """Inspect signals that exist but are not yet readable.

        This method is instrumentation for experiments.  A local node should not
        receive it unless the experiment explicitly grants that ability.
        """
        signals = [item[2] for item in self._queue]
        if target is not None:
            signals = [s for s in signals if s.target == target]
        return sorted(signals, key=lambda s: s.available_at)

    def local_state(self, node: str) -> Dict[str, Any]:
        """Small diagnostic view of one receiver's present."""
        inbox = list(self._inboxes.get(node, ()))
        return {
            "now": self.now,
            "readable_count": len(inbox),
            "readable_kinds": [s.kind for s in inbox],
        }
