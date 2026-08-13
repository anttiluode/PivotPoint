import asyncio
import unittest

from pivotpoint.work import WorkStatus
from pivotpoint.workers import AsyncWorkerPool


class AsyncWorkerPoolTests(unittest.IsolatedAsyncioTestCase):
    async def test_result_does_not_exist_while_worker_is_blocked(self):
        gate = asyncio.Event()
        pool = AsyncWorkerPool()

        async def worker():
            await gate.wait()
            return "done"

        item = pool.submit(
            worker(), owner="planner", target="planner", kind="refresh"
        )
        await asyncio.sleep(0)

        self.assertEqual(item.status, WorkStatus.PENDING)
        self.assertIsNone(item.result)
        self.assertEqual(
            pool.registry.local_state("planner", now=pool.clock())["pending_count"],
            1,
        )

        gate.set()
        await pool.wait(item.work_id)
        self.assertEqual(item.status, WorkStatus.SUCCEEDED)
        self.assertEqual(item.result, "done")

    async def test_fast_result_can_be_read_while_slow_work_is_still_pending(self):
        slow_gate = asyncio.Event()
        pool = AsyncWorkerPool()

        async def fast():
            await asyncio.sleep(0)
            return "fast"

        async def slow():
            await slow_gate.wait()
            return "slow"

        fast_item = pool.submit(fast(), owner="a", target="pivot", kind="fast")
        slow_item = pool.submit(slow(), owner="b", target="pivot", kind="slow")

        await pool.wait(fast_item.work_id)
        self.assertEqual(fast_item.status, WorkStatus.SUCCEEDED)
        self.assertEqual(slow_item.status, WorkStatus.PENDING)

        result = pool.registry.consume(
            fast_item.work_id, target="pivot", now=pool.clock()
        )
        self.assertEqual(result, "fast")
        self.assertEqual(slow_item.status, WorkStatus.PENDING)

        slow_gate.set()
        await pool.wait(slow_item.work_id)
        self.assertEqual(slow_item.status, WorkStatus.SUCCEEDED)

    async def test_worker_exception_becomes_failed_work_state(self):
        pool = AsyncWorkerPool()

        async def broken():
            raise ValueError("bad")

        item = pool.submit(broken(), owner="x", target="pivot", kind="probe")
        await pool.wait(item.work_id)

        self.assertEqual(item.status, WorkStatus.FAILED)
        self.assertIn("ValueError", item.error)
        self.assertIn("bad", item.error)

    async def test_cancellation_is_explicit_state(self):
        gate = asyncio.Event()
        pool = AsyncWorkerPool()

        async def slow():
            await gate.wait()
            return 1

        item = pool.submit(slow(), owner="x", target="pivot", kind="probe")
        await asyncio.sleep(0)
        pool.cancel(item.work_id)
        await pool.wait(item.work_id)

        self.assertEqual(item.status, WorkStatus.CANCELLED)


if __name__ == "__main__":
    unittest.main()
