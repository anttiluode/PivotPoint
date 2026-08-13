"""Minimal asyncio worker adapter for PivotPoint.

This module is intentionally boring. ``asyncio`` already knows how to run
concurrent work; PivotPoint should not pretend to have invented a scheduler.
The adapter's only job is to keep the explicit WorkRegistry synchronized with
real unfinished computation so a local controller can distinguish:

- no work requested;
- work pending, result not yet existent;
- result completed but not yet consumed;
- failure/cancellation.

A smarter policy must beat ordinary asyncio/queue baselines later.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any, Awaitable, Callable, Dict, Mapping, Optional

from .work import WorkItem, WorkRegistry, WorkStatus


class AsyncWorkerPool:
    """Run awaitables while mirroring their lifecycle into ``WorkRegistry``."""

    def __init__(
        self,
        registry: Optional[WorkRegistry] = None,
        *,
        clock: Callable[[], float] = time.perf_counter,
    ) -> None:
        self.registry = registry or WorkRegistry()
        self.clock = clock
        self._tasks: Dict[str, asyncio.Task[None]] = {}

    def submit(
        self,
        awaitable: Awaitable[Any],
        *,
        owner: str,
        target: str,
        kind: str,
        expected_seconds: Optional[float] = None,
        work_id: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> WorkItem:
        """Start real asynchronous work and return its explicit work ticket."""
        started = float(self.clock())
        expected_ready_at = (
            None
            if expected_seconds is None
            else started + max(0.0, float(expected_seconds))
        )
        item = self.registry.start(
            owner=owner,
            target=target,
            kind=kind,
            started_at=started,
            expected_ready_at=expected_ready_at,
            work_id=work_id,
            metadata=metadata,
        )
        self._tasks[item.work_id] = asyncio.create_task(
            self._drive(item.work_id, awaitable)
        )
        return item

    def submit_blocking(
        self,
        func: Callable[..., Any],
        *args: Any,
        owner: str,
        target: str,
        kind: str,
        expected_seconds: Optional[float] = None,
        work_id: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
        **kwargs: Any,
    ) -> WorkItem:
        """Run a blocking callable in asyncio's thread helper."""

        async def invoke() -> Any:
            return await asyncio.to_thread(func, *args, **kwargs)

        return self.submit(
            invoke(),
            owner=owner,
            target=target,
            kind=kind,
            expected_seconds=expected_seconds,
            work_id=work_id,
            metadata=metadata,
        )

    async def _drive(self, work_id: str, awaitable: Awaitable[Any]) -> None:
        try:
            result = await awaitable
        except asyncio.CancelledError:
            item = self.registry.get(work_id)
            if item.status == WorkStatus.PENDING:
                self.registry.cancel(work_id, now=self.clock())
            raise
        except Exception as exc:  # worker failure belongs in state, not task logs only
            item = self.registry.get(work_id)
            if item.status == WorkStatus.PENDING:
                self.registry.fail(
                    work_id,
                    error=f"{type(exc).__name__}: {exc}",
                    now=self.clock(),
                )
        else:
            item = self.registry.get(work_id)
            if item.status == WorkStatus.PENDING:
                self.registry.succeed(work_id, result=result, now=self.clock())

    def task(self, work_id: str) -> asyncio.Task[None]:
        try:
            return self._tasks[work_id]
        except KeyError as exc:
            raise KeyError(f"unknown worker task: {work_id}") from exc

    def cancel(self, work_id: str) -> bool:
        """Request cancellation. The registry changes state when task handles it."""
        return self.task(work_id).cancel()

    async def wait(self, work_id: str) -> WorkItem:
        task = self.task(work_id)
        try:
            await task
        except asyncio.CancelledError:
            pass
        return self.registry.get(work_id)

    async def wait_all(self) -> Dict[str, WorkItem]:
        ids = list(self._tasks)
        await asyncio.gather(
            *(self.wait(work_id) for work_id in ids),
            return_exceptions=False,
        )
        return {work_id: self.registry.get(work_id) for work_id in ids}
