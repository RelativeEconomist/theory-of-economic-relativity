"""
Framework test: single-unit allocation

Purpose
-------
Not an economic replication test. Verifies
research.ter.market.allocate_single_unit in isolation: it is a small,
scenario-agnostic scarcity resolution helper (see
test_25_multi_agent_system_outcome.py for its use inside a reality
function), not a TER primitive and not a general market-clearing engine.

A unique highest bid must win outright. A tie for the highest bid must
not be resolved silently (e.g. by dict iteration order) -- it must raise,
so any tie-breaking rule remains an explicit choice a caller makes, not
one this helper makes for them.
"""

import unittest

from research.ter.market import allocate_single_unit


class TestSingleUnitAllocation(unittest.TestCase):
    TEST_NAME = "Framework: Single-Unit Allocation"

    def test_unique_highest_bid_wins(self):
        winner = allocate_single_unit(
            {
                "buyer_a": 8,
                "buyer_b": 10,
            }
        )

        self.assertEqual(
            winner,
            "buyer_b",
        )

    def test_tied_highest_bid_raises_value_error(self):
        with self.assertRaises(ValueError):
            allocate_single_unit(
                {
                    "buyer_a": 10,
                    "buyer_b": 10,
                }
            )
