"""
Framework test: public rule enums.

Purpose
-------
This is not an economic replication test. It verifies the researcher-facing
API itself: every member of DecisionProcess, ValuationRule, RealityFunction, and
FeedbackRule (research/ter/__init__.py) must resolve through the existing
rule registry (research/ter/rules.py) to the exact same callable as its
underlying string, and framework internals must not be part of the public
research.ter surface.

Assumptions
-----------
- Enum values are a naming convenience over the existing string-keyed
  registry, not a second registration mechanism. This test exists to catch
  drift if a rule is ever renamed or removed without updating its enum.
- capacity_constrained_realization (registered locally in
  test_feasibility_contract.py) is intentionally not part of any public
  enum and is not checked here.
"""

import unittest

from research.ter import (
    AgentResult,
    AgentSpec,
    DecisionProcess,
    FeedbackRule,
    RealityFunction,
    Scenario,
    ScenarioResult,
    ValuationRule,
    run_scenario,
)
from research.ter.rules import RULES, get_rule


ALL_PUBLIC_RULE_ENUMS = (
    DecisionProcess,
    ValuationRule,
    RealityFunction,
    FeedbackRule,
)


class TestPublicRuleEnums(unittest.TestCase):
    TEST_NAME = "Framework: Public Rule Enums"

    def test_every_enum_member_resolves_through_the_registry(self):
        for enum_class in ALL_PUBLIC_RULE_ENUMS:
            for member in enum_class:
                self.assertIn(
                    member.value,
                    RULES,
                    f"{enum_class.__name__}.{member.name} = {member.value!r} "
                    "is not a registered rule.",
                )

    def test_enum_member_resolves_to_the_same_callable_as_its_string(self):
        for enum_class in ALL_PUBLIC_RULE_ENUMS:
            for member in enum_class:
                self.assertIs(
                    get_rule(member),
                    get_rule(member.value),
                )

    def test_enum_members_are_valid_strings(self):
        for enum_class in ALL_PUBLIC_RULE_ENUMS:
            for member in enum_class:
                self.assertIsInstance(
                    member,
                    str,
                )

                self.assertEqual(
                    member,
                    member.value,
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
            "DecisionProcess",
            "ValuationRule",
            "RealityFunction",
            "FeedbackRule",
            "run_scenario",
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
            "register_rule",
            "get_rule",
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
