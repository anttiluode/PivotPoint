import unittest

from pivotpoint import ActionOffer, Edge, PivotPolicy, PivotRuntime


class PivotRuntimeTests(unittest.TestCase):
    def test_signal_is_not_readable_before_route_delay(self):
        rt = PivotRuntime()
        rt.connect(Edge("source", "receiver", delay=2.0))
        rt.emit("source", {"x": 1})

        rt.advance(1.0)
        self.assertEqual(rt.read("receiver"), [])

        rt.advance(1.0)
        got = rt.read("receiver")
        self.assertEqual(len(got), 1)
        self.assertEqual(got[0].payload, {"x": 1})
        self.assertAlmostEqual(got[0].age_when_available, 2.0)

    def test_modulator_changes_effective_edge_gain_without_rewiring(self):
        rt = PivotRuntime()
        rt.connect(
            Edge(
                "source",
                "receiver",
                base_gain=1.0,
                receptors={"gate": 1.0},
            )
        )

        rt.modulators.set("gate", 0.0)
        rt.emit("source", "a")
        rt.advance(0.0)
        base = rt.read("receiver")[0].strength

        rt.modulators.set("gate", 1.0)
        rt.emit("source", "b")
        rt.advance(0.0)
        boosted = rt.read("receiver")[0].strength

        self.assertGreater(boosted, base)

    def test_policy_can_prefer_accessibility_gain_over_raw_value(self):
        policy = PivotPolicy(
            value_weight=1.0,
            accessibility_weight=2.0,
            cost_weight=1.0,
            risk_weight=1.0,
        )
        direct = ActionOffer(
            owner="planner",
            action="act_now",
            expected_value=2.0,
            expected_accessibility_gain=0.0,
            cost=0.1,
        )
        probe = ActionOffer(
            owner="probe",
            action="measure",
            expected_value=0.5,
            expected_accessibility_gain=1.0,
            cost=0.1,
        )

        choice = policy.choose([direct, probe])
        self.assertIsNotNone(choice)
        self.assertEqual(choice.offer.action, "measure")


if __name__ == "__main__":
    unittest.main()
