"""
Framework test: TER simulation Cloudflare Worker.

Purpose
-------
This is not an economic replication test. It calls the Worker's fetch
handler directly and checks that the production transport rules (one
allowed origin, a bounded body, a per-IP rate limit, JSON errors) wrap
exactly what the scenario's JSON-safe adapter returns, never economics.

The `workers` module exists only inside the Cloudflare runtime, so the
Worker is imported here against stand-ins for the two names it uses.
"""

import asyncio
import json
import sys
import types
import unittest
from http.client import HTTPMessage
from unittest.mock import patch

from applications.api.endpoint import MAX_BODY_BYTES, PATH
from research.adapters import asymmetric_information, feasible_set_learning, pokemon_card_choice
from research.adapters.basic_agent_choice import SCENARIO_ID, run

PRODUCTION_ORIGIN = "https://www.theoryofeconomicrelativity.com"
CLIENT_IP = "203.0.113.7"
CONFIGURED_VALUES = {"coffee_a": 9, "coffee_b": 7.5, "coffee_c": 1}
DEFAULT_BODY = json.dumps({"scenario": SCENARIO_ID, "inputs": {}}).encode()

# The methods the Workers SDK names; its Request.method raises KeyError for others.
STANDARD_METHODS = frozenset(
    {"CONNECT", "DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT", "TRACE"}
)


class FakeResponse:
    def __init__(self, body=None, status=200, headers=None):
        self.body = body
        self.status = status
        self.headers = headers or {}

    def json(self):
        return json.loads(self.body)


class FakeWorkerEntrypoint:
    def __init__(self, ctx, env):
        self.ctx = ctx
        self.env = env


with patch.dict(
    sys.modules,
    {
        "workers": types.SimpleNamespace(
            Response=FakeResponse, WorkerEntrypoint=FakeWorkerEntrypoint
        )
    },
):
    from applications.api.worker import MAX_JSON_DEPTH, Default


class FakeRequest:
    """
    A request as the Workers SDK presents it. content_length defaults to the
    body's real length; pass None to send no Content-Length header.
    """

    def __init__(
        self,
        body=DEFAULT_BODY,
        method="POST",
        path=PATH,
        origin=PRODUCTION_ORIGIN,
        content_length="actual",
    ):
        self.raw_method = method
        self.url = "https://api.theoryofeconomicrelativity.com" + path
        self.body = body
        self.body_was_read = False
        self.headers = HTTPMessage()
        self.headers["Origin"] = origin
        self.headers["CF-Connecting-IP"] = CLIENT_IP

        if content_length == "actual":
            content_length = str(len(body))

        if content_length is not None:
            self.headers["Content-Length"] = content_length

    @property
    def method(self):
        if self.raw_method not in STANDARD_METHODS:
            raise KeyError(self.raw_method)

        return self.raw_method

    async def bytes(self):
        self.body_was_read = True
        return self.body


class FakeRateLimiter:
    """Stands in for the Wrangler rate-limit binding; records each charged key."""

    def __init__(self, success=True):
        self.success = success
        self.charged_keys = []

    async def limit(self, *, key):
        self.charged_keys.append(key)
        return types.SimpleNamespace(success=self.success)


def fetch(request, rate_limiter=None, allowed_origin=PRODUCTION_ORIGIN):
    """Run the Worker's fetch handler for request and return its response."""
    env = types.SimpleNamespace(
        TER_ALLOWED_ORIGIN=allowed_origin,
        SIMULATE_RATE_LIMITER=rate_limiter or FakeRateLimiter(),
    )

    return asyncio.run(Default(None, env).fetch(request))


class TestSimulationWorker(unittest.TestCase):
    TEST_NAME = "Framework: Simulation Worker"

    def assert_json_error(self, response, status, expected):
        """Every Worker error is a JSON body of exactly {"error": message}."""
        self.assertEqual(response.status, status)
        self.assertEqual(response.headers["Content-Type"], "application/json")

        body = response.json()

        self.assertEqual(list(body), ["error"])
        self.assertIn(expected, body["error"])

    def test_envelopes_match_the_direct_adapter_run(self):
        # The Worker passes the parsed envelope to endpoint.simulate, the
        # same routing the local server uses; per-scenario routing is
        # tested once, in test_simulation_http.py.
        for inputs in ({}, {"action_values": CONFIGURED_VALUES}):
            with self.subTest(inputs=inputs):
                body = json.dumps({"scenario": SCENARIO_ID, "inputs": inputs}).encode()

                response = fetch(FakeRequest(body))

                self.assertEqual(response.status, 200)
                self.assertEqual(response.headers["Content-Type"], "application/json")
                self.assertEqual(response.json(), run({"scenario": SCENARIO_ID, **inputs}))

    def test_pokemon_reaches_the_registered_adapter(self):
        for inputs in ({}, {"buyer_available": False}, {"keep_value": 300}):
            with self.subTest(inputs=inputs):
                request = {"scenario": pokemon_card_choice.SCENARIO_ID, "inputs": inputs}
                response = fetch(FakeRequest(json.dumps(request).encode()))
                self.assertEqual(response.status, 200)
                self.assertEqual(response.json(), pokemon_card_choice.run({"scenario": pokemon_card_choice.SCENARIO_ID, **inputs}))
        invalid = {"scenario": pokemon_card_choice.SCENARIO_ID, "inputs": {"buyer_available": 1}}
        self.assert_json_error(fetch(FakeRequest(json.dumps(invalid).encode())), 400, "boolean")

    def test_rejected_requests_return_the_endpoint_or_adapter_error(self):
        for request, expected in (
            (["basic-agent-choice"], "JSON object"),
            ({"scenario": SCENARIO_ID}, "'inputs'"),
            ({"scenario": "other-scenario", "inputs": {}}, "Unsupported scenario"),
            ({"scenario": SCENARIO_ID, "inputs": {"action_values": {"coffee_a": 1}}}, "action_values"),
            (
                {"scenario": asymmetric_information.SCENARIO_ID, "inputs": {"pricing": "other"}},
                "pricing",
            ),
            (
                {"scenario": feasible_set_learning.SCENARIO_ID, "inputs": {"periods": 3}},
                "'periods'",
            ),
        ):
            with self.subTest(request=request):
                response = fetch(FakeRequest(json.dumps(request).encode()))

                self.assert_json_error(response, 400, expected)

    def test_malformed_json_returns_a_json_400(self):
        for raw in (b"{not json", b"", b"\xff"):
            with self.subTest(raw=raw):
                self.assert_json_error(fetch(FakeRequest(raw)), 400, "JSON")

    def test_json_nested_past_the_limit_returns_a_json_400_without_parsing(self):
        too_deep = MAX_JSON_DEPTH + 1

        for raw in (
            "[" * too_deep + "]" * too_deep,
            '{"a":' * too_deep + "1" + "}" * too_deep,
            '{"scenario":"%s","inputs":%s}' % (SCENARIO_ID, "[" * MAX_JSON_DEPTH),
            # Unclosed, and deep enough to kill the Worker runtime if parsed.
            "[" * 30000,
            # The escaped backslash ends its string, so the nesting after it counts.
            '["\\\\",' + "[" * MAX_JSON_DEPTH,
        ):
            with self.subTest(raw=raw[:40]):
                with patch.object(json, "loads") as loads:
                    response = fetch(FakeRequest(raw.encode()))

                loads.assert_not_called()
                self.assert_json_error(response, 400, f"deeper than {MAX_JSON_DEPTH} levels")

    def test_allowed_nesting_and_brackets_inside_strings_reach_the_endpoint(self):
        brackets = "[{" * MAX_JSON_DEPTH

        for raw, expected in (
            ("[" * MAX_JSON_DEPTH + "]" * MAX_JSON_DEPTH, "JSON object"),
            (json.dumps({"scenario": brackets, "inputs": {}}), "Unsupported scenario"),
            # An escaped quote does not end its string.
            (json.dumps({"scenario": '"' + brackets, "inputs": {}}), "Unsupported scenario"),
        ):
            with self.subTest(raw=raw[:40]):
                self.assert_json_error(fetch(FakeRequest(raw.encode())), 400, expected)

    def test_unsupported_routes_return_a_json_404(self):
        for path in ("/", "/basic-agent-choice", "/simulate/"):
            for method in ("POST", "OPTIONS", "GET"):
                with self.subTest(path=path, method=method):
                    response = fetch(FakeRequest(path=path, method=method))

                    self.assert_json_error(response, 404, PATH)

    def test_unsupported_methods_return_a_json_405_without_running(self):
        for method in ("GET", "PUT", "DELETE", "PROPFIND"):
            with self.subTest(method=method):
                request = FakeRequest(method=method)
                rate_limiter = FakeRateLimiter()

                response = fetch(request, rate_limiter)

                self.assert_json_error(response, 405, "POST")
                self.assertEqual(response.headers["Allow"], "POST, OPTIONS")
                self.assertFalse(request.body_was_read)
                self.assertEqual(rate_limiter.charged_keys, [])

    def test_oversized_declared_length_returns_a_json_413_without_reading(self):
        # The last two are longer than Python's default int-from-str digit limit.
        for content_length in (
            str(MAX_BODY_BYTES + 1),
            str(10 * 1024 * 1024),
            "9" * 5000,
            "0" * 5000 + "65537",
        ):
            with self.subTest(digits=len(content_length)):
                request = FakeRequest(content_length=content_length)

                response = fetch(request)

                self.assert_json_error(response, 413, str(MAX_BODY_BYTES))
                self.assertFalse(request.body_was_read)

    def test_missing_or_malformed_length_is_rejected_without_reading(self):
        for content_length, status in (
            (None, 411),
            ("abc", 400),
            ("1.5", 400),
            ("-1", 400),
            ("", 400),
            ("10, 10", 400),
        ):
            with self.subTest(content_length=content_length):
                request = FakeRequest(content_length=content_length)

                response = fetch(request)

                self.assert_json_error(response, status, "Content-Length")
                self.assertFalse(request.body_was_read)

    def test_oversized_actual_body_returns_a_json_413(self):
        # A body larger than its declared length is still refused.
        request = FakeRequest(b" " * (MAX_BODY_BYTES + 1), content_length="10")

        self.assert_json_error(fetch(request), 413, str(MAX_BODY_BYTES))

        # A body exactly at the limit is read and parsed.
        request = FakeRequest(b" " * MAX_BODY_BYTES)

        self.assert_json_error(fetch(request), 400, "JSON")
        self.assertTrue(request.body_was_read)

    def assert_origin_allowed(self, response):
        self.assertEqual(response.headers["Access-Control-Allow-Origin"], PRODUCTION_ORIGIN)
        self.assertEqual(response.headers["Vary"], "Origin")

    def test_production_origin_is_allowed(self):
        preflight = fetch(FakeRequest(None, method="OPTIONS", content_length=None))

        self.assertEqual(preflight.status, 204)
        self.assertIsNone(preflight.body)
        self.assert_origin_allowed(preflight)
        self.assertIn("POST", preflight.headers["Access-Control-Allow-Methods"])
        self.assertIn("Content-Type", preflight.headers["Access-Control-Allow-Headers"])

        # Errors carry the header too, so the page can read the JSON error.
        for request in (FakeRequest(), FakeRequest(b"{not json"), FakeRequest(path="/other")):
            with self.subTest(url=request.url, body=request.body):
                self.assert_origin_allowed(fetch(request))

    def test_other_origins_are_not_allowed(self):
        for origin in (
            # The local Astro origins are for the local server only.
            "http://localhost:4321",
            "http://127.0.0.1:4321",
            "https://theoryofeconomicrelativity.com",
            "http://www.theoryofeconomicrelativity.com",
            "https://www.theoryofeconomicrelativity.com:8443",
            "https://www.theoryofeconomicrelativity.com.evil.com",
            "https://example.com",
            "null",
        ):
            for request in (
                FakeRequest(None, method="OPTIONS", origin=origin, content_length=None),
                FakeRequest(origin=origin),
            ):
                with self.subTest(origin=origin, method=request.raw_method):
                    response = fetch(request)

                    self.assertNotIn("Access-Control-Allow-Origin", response.headers)

    def test_invalid_configured_origin_returns_a_json_500(self):
        for allowed_origin in ("*", "https://*.theoryofeconomicrelativity.com", PRODUCTION_ORIGIN + "/"):
            with self.subTest(allowed_origin=allowed_origin):
                request = FakeRequest(origin=allowed_origin)

                response = fetch(request, allowed_origin=allowed_origin)

                self.assert_json_error(response, 500, "TER_ALLOWED_ORIGIN")
                self.assertNotIn("Access-Control-Allow-Origin", response.headers)
                self.assertFalse(request.body_was_read)

    def test_rate_limited_post_returns_a_json_429_without_running(self):
        request = FakeRequest()
        rate_limiter = FakeRateLimiter(success=False)

        response = fetch(request, rate_limiter)

        self.assert_json_error(response, 429, "Too many requests")
        self.assert_origin_allowed(response)
        self.assertFalse(request.body_was_read)
        self.assertEqual(rate_limiter.charged_keys, [CLIENT_IP])

    def test_each_post_is_charged_once_to_the_client_ip_and_preflights_are_free(self):
        rate_limiter = FakeRateLimiter()

        fetch(FakeRequest(None, method="OPTIONS", content_length=None), rate_limiter)
        self.assertEqual(rate_limiter.charged_keys, [])

        self.assertEqual(fetch(FakeRequest(), rate_limiter).status, 200)
        self.assertEqual(rate_limiter.charged_keys, [CLIENT_IP])


if __name__ == "__main__":
    unittest.main()
