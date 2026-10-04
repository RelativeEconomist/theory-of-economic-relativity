"""
Framework test: public TER surface.

Purpose
-------
This is not an economic replication test. It verifies the intentionally small
researcher-facing API and keeps execution internals out of that surface.
"""

import unittest

from research.ter import (
    AgentResult,
    AgentSpec,
    Scenario,
    ScenarioResult,
    run_scenario,
)


class TestPublicSurface(unittest.TestCase):
    TEST_NAME = "Framework: Public Surface"

    def test_expected_names_are_exported(self):
        import research.ter as public_api

        expected = {
            "AgentSpec",
            "AgentGroup",
            "Scenario",
            "ScenarioResult",
            "AgentResult",
            "RealityResult",
            "Schedule",
            "run_scenario",
            "__version__",
        }

        self.assertEqual(
            set(public_api.__all__),
            expected,
        )

        for name in expected:
            self.assertTrue(
                hasattr(public_api, name),
            )

    def test_internals_are_not_part_of_the_public_surface(self):
        import research.ter as public_api

        internals = {
            "AgentState",
            "build_agent",
            "select_action",
        }

        for name in internals:
            self.assertNotIn(
                name,
                public_api.__all__,
            )

            self.assertFalse(
                hasattr(public_api, name),
                f"{name} should not be directly accessible on research.ter",
            )
