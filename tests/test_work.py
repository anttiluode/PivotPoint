import unittest

from pivotpoint.work import WorkRegistry, WorkStatus


class WorkRegistryTests(unittest.TestCase):
    def test_pending_work_has_no_result_yet(self):
        work = WorkRegistry()
        item = work.start(
            owner="planner",
            target="planner",
            kind="refresh",
            started_at=10.0,
            expected_ready_at=13.0,
        )

        self.assertEqual(item.status, WorkStatus.PENDING)
        self.assertTrue(item.in_flight)
        self.assertFalse(item.unread_result)
        self.assertIsNone(item.result)

        state = work.local_state("planner", now=11.0)
        self.assertEqual(state["pending_count"], 1)
        self.assertAlmostEqual(state["earliest_known_eta"], 2.0)

    def test_success_is_distinct_from_consumption(self):
        work = WorkRegistry()
        item = work.start(
            owner="retriever",
            target="planner",
            kind="document",
            started_at=0.0,
        )
        work.succeed(item.work_id, result={"answer": 42}, now=2.5)

        planner = work.local_state("planner", now=2.5)
        self.assertEqual(planner["pending_count"], 0)
        self.assertEqual(planner["unread_result_count"], 1)

        result = work.consume(item.work_id, target="planner", now=3.0)
        self.assertEqual(result, {"answer": 42})
        self.assertEqual(item.status, WorkStatus.CONSUMED)
        self.assertEqual(work.local_state("planner", now=3.0)["unread_result_count"], 0)

    def test_wrong_receiver_cannot_consume_result(self):
        work = WorkRegistry()
        item = work.start(
            owner="sensor",
            target="controller",
            kind="measurement",
            started_at=0.0,
        )
        work.succeed(item.work_id, result=1.0, now=1.0)

        with self.assertRaises(PermissionError):
            work.consume(item.work_id, target="other", now=1.0)

    def test_terminal_work_cannot_be_completed_twice(self):
        work = WorkRegistry()
        item = work.start(
            owner="worker",
            target="planner",
            kind="test",
            started_at=0.0,
        )
        work.fail(item.work_id, error="boom", now=1.0)
        self.assertEqual(item.status, WorkStatus.FAILED)

        with self.assertRaises(RuntimeError):
            work.succeed(item.work_id, result="late", now=2.0)

    def test_local_state_is_not_global_process_table(self):
        work = WorkRegistry()
        work.start(
            owner="a",
            target="a",
            kind="own",
            started_at=0.0,
        )
        work.start(
            owner="b",
            target="c",
            kind="foreign",
            started_at=0.0,
        )

        self.assertEqual(work.local_state("a", now=0.0)["pending_kinds"], ["own"])
        self.assertEqual(work.local_state("z", now=0.0)["pending_count"], 0)


if __name__ == "__main__":
    unittest.main()
