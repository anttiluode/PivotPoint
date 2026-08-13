"""Explicit state for work that has started but is not finished yet.

PivotPoint distinguishes a delayed *message* from unfinished *work*.
A Signal already has a payload and is only waiting for its route delay. A
WorkItem may have no result at all yet: a test is still running, a model is
still decoding, a sensor exposure is still integrating, or a remote request is
still pending.

The registry is deliberately executor-agnostic. It records the process-present
state without deciding whether work runs in a thread, process, GPU, service, or
human loop.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Mapping, Optional


class WorkStatus(str, Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    CONSUMED = "consumed"


@dataclass
class WorkItem:
    work_id: str
    owner: str
    target: str
    kind: str
    started_at: float
    expected_ready_at: Optional[float] = None
    status: WorkStatus = WorkStatus.PENDING
    completed_at: Optional[float] = None
    consumed_at: Optional[float] = None
    result: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def in_flight(self) -> bool:
        return self.status == WorkStatus.PENDING

    @property
    def unread_result(self) -> bool:
        return self.status == WorkStatus.SUCCEEDED

    def age(self, now: float) -> float:
        return max(0.0, float(now) - float(self.started_at))

    def eta(self, now: float) -> Optional[float]:
        if self.expected_ready_at is None or not self.in_flight:
            return None
        return max(0.0, float(self.expected_ready_at) - float(now))


class WorkRegistry:
    """Bookkeeping for unfinished and newly completed work.

    The registry does not run jobs. It makes a distinction that completed
    transcripts erase: "nothing has been requested" versus "a result is already
    becoming but is not readable yet".

    Visibility is explicit. ``local_state(node, now)`` only includes work for
    which ``node`` is the owner or intended target; it is not a global process
    table smuggled into every local controller.
    """

    def __init__(self) -> None:
        self._items: Dict[str, WorkItem] = {}
        self._counter = 0

    def start(
        self,
        *,
        owner: str,
        target: str,
        kind: str,
        started_at: float,
        expected_ready_at: Optional[float] = None,
        work_id: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> WorkItem:
        if work_id is None:
            self._counter += 1
            work_id = f"work-{self._counter}"
        if work_id in self._items:
            raise ValueError(f"duplicate work_id: {work_id}")
        if expected_ready_at is not None and expected_ready_at < started_at:
            raise ValueError("expected_ready_at cannot precede started_at")

        item = WorkItem(
            work_id=str(work_id),
            owner=str(owner),
            target=str(target),
            kind=str(kind),
            started_at=float(started_at),
            expected_ready_at=(
                None if expected_ready_at is None else float(expected_ready_at)
            ),
            metadata=dict(metadata or {}),
        )
        self._items[item.work_id] = item
        return item

    def get(self, work_id: str) -> WorkItem:
        try:
            return self._items[work_id]
        except KeyError as exc:
            raise KeyError(f"unknown work_id: {work_id}") from exc

    def succeed(self, work_id: str, *, result: Any, now: float) -> WorkItem:
        item = self.get(work_id)
        self._require_pending(item)
        item.status = WorkStatus.SUCCEEDED
        item.completed_at = float(now)
        item.result = result
        item.error = None
        return item

    def fail(self, work_id: str, *, error: str, now: float) -> WorkItem:
        item = self.get(work_id)
        self._require_pending(item)
        item.status = WorkStatus.FAILED
        item.completed_at = float(now)
        item.error = str(error)
        item.result = None
        return item

    def cancel(self, work_id: str, *, now: float) -> WorkItem:
        item = self.get(work_id)
        self._require_pending(item)
        item.status = WorkStatus.CANCELLED
        item.completed_at = float(now)
        item.result = None
        return item

    def consume(self, work_id: str, *, target: str, now: float) -> Any:
        item = self.get(work_id)
        if item.target != target:
            raise PermissionError(
                f"work {work_id} targets {item.target!r}, not {target!r}"
            )
        if item.status != WorkStatus.SUCCEEDED:
            raise RuntimeError(
                f"work {work_id} is not a readable successful result: "
                f"{item.status.value}"
            )
        result = item.result
        item.status = WorkStatus.CONSUMED
        item.consumed_at = float(now)
        return result

    def items(
        self,
        *,
        status: Optional[WorkStatus] = None,
        owner: Optional[str] = None,
        target: Optional[str] = None,
    ) -> List[WorkItem]:
        out = list(self._items.values())
        if status is not None:
            out = [item for item in out if item.status == status]
        if owner is not None:
            out = [item for item in out if item.owner == owner]
        if target is not None:
            out = [item for item in out if item.target == target]
        return sorted(out, key=lambda item: (item.started_at, item.work_id))

    def local_state(self, node: str, *, now: float) -> Dict[str, Any]:
        visible = [
            item for item in self._items.values()
            if item.owner == node or item.target == node
        ]
        pending = [item for item in visible if item.status == WorkStatus.PENDING]
        unread = [item for item in visible if item.status == WorkStatus.SUCCEEDED]
        failed = [item for item in visible if item.status == WorkStatus.FAILED]

        etas = [item.eta(now) for item in pending]
        known_etas = [eta for eta in etas if eta is not None]

        return {
            "pending_count": len(pending),
            "pending_kinds": [item.kind for item in pending],
            "unread_result_count": len(unread),
            "unread_result_kinds": [item.kind for item in unread],
            "failed_count": len(failed),
            "earliest_known_eta": min(known_etas) if known_etas else None,
        }

    @staticmethod
    def _require_pending(item: WorkItem) -> None:
        if item.status != WorkStatus.PENDING:
            raise RuntimeError(
                f"work {item.work_id} is not pending: {item.status.value}"
            )
