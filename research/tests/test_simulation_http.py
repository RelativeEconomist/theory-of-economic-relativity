"""
Framework test: centralized TER simulation HTTP endpoint.

Purpose
-------
This is not an economic replication test. It runs the real local HTTP
server and checks that POST /simulate returns exactly what the scenario's
JSON-safe adapter returns, so the browser path adds transport only, never
economics.
"""

import json
import threading
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from research.adapters.basic_agent_choice import SCENARIO_ID, run
from research.http.simulation import PATH, SimulationHandler, allowed_origins

DEV_ORIGIN = "http://localhost:4321"
ALLOWED_ORIGINS = (DEV_ORIGIN, "http://127.0.0.1:4321")
PRODUCTION_ORIGIN = "https://ter.example.org"
BODY_LIMIT = 64 * 1024
CONFIGURED_VALUES = {"coffee_a": 9, "coffee_b": 7.5, "coffee_c": 1}


class QuietHandler(SimulationHandler):
    # Short enough that the request-timeout test stays fast.
    timeout = 0.5

    def log_message(self, format, *args):
        pass


class ProductionHandler(QuietHandler):
    # As if started with TER_ALLOWED_ORIGIN=PRODUCTION_ORIGIN.
    cors_origins = allowed_origins(PRODUCTION_ORIGIN)


class TestSimulationHttp(unittest.TestCase):
    TEST_NAME = "Framework: Simulation HTTP Endpoint"

    @classmethod
    def setUpClass(cls):
        cls.host, cls.port = cls.start_server(QuietHandler)
        cls.base_url = f"http://{cls.host}:{cls.port}"
        production_host, production_port = cls.start_server(ProductionHandler)
        cls.production_url = f"http://{production_host}:{production_port}"

    @classmethod
    def start_server(cls, handler):
        """Serve handler on a free local port until the class finishes."""
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        # Cleanups run last-in, first-out: shutdown, close, then join.
        cls.addClassCleanup(thread.join)
        cls.addClassCleanup(server.server_close)
        cls.addClassCleanup(server.shutdown)

        return server.server_address[:2]

    def send(
        self, body, method="POST", path="/simulate", origin=DEV_ORIGIN, base_url=None
    ):
        """Send a request; return (status, headers, parsed JSON body or None)."""
        headers = {"Origin": origin}
        if body is not None:
            headers["Content-Type"] = "application/json"

        request = Request(
            (base_url or self.base_url) + path, data=body, headers=headers, method=method
        )

        try:
            with urlopen(request, timeout=5) as response:
                status, headers, raw = response.status, response.headers, response.read()
        except HTTPError as error:
            status, headers, raw = error.code, error.headers, error.read()

        return status, headers, json.loads(raw) if raw else None

    def post_json(self, payload, path="/simulate"):
        return self.send(json.dumps(payload).encode(), path=path)

    def post_headers_only(self, *content_lengths):
        """
        POST /simulate with one exact Content-Length header line per value
        and no body; return (status, parsed JSON body). A server that tries
        to read the declared body times out here instead of answering.
        """
        connection = HTTPConnection(self.host, self.port, timeout=5)

        try:
            connection.putrequest("POST", PATH)
            connection.putheader("Content-Type", "application/json")
            for content_length in content_lengths:
                connection.putheader("Content-Length", content_length)
            connection.endheaders()
            response = connection.getresponse()
            return response.status, json.loads(response.read())
        finally:
            connection.close()

    def test_envelopes_match_the_direct_adapter_run(self):
        # The envelope's inputs become the adapter request's other keys.
        for inputs in ({}, {"action_values": CONFIGURED_VALUES}):
            with self.subTest(inputs=inputs):
                status, headers, body = self.post_json(
                    {"scenario": SCENARIO_ID, "inputs": inputs}
                )

                self.assertEqual(status, 200)
                self.assertEqual(headers["Content-Type"], "application/json")
                self.assertEqual(body, run({"scenario": SCENARIO_ID, **inputs}))

    def test_invalid_envelopes_are_rejected(self):
        for request, expected in (
            (["basic-agent-choice"], "JSON object"),
            ({"scenario": SCENARIO_ID}, "'inputs'"),
            ({"inputs": {}}, "'scenario'"),
            (
                {"scenario": SCENARIO_ID, "inputs": {}, "action_values": CONFIGURED_VALUES},
                "'action_values'",
            ),
            ({"scenario": SCENARIO_ID, "inputs": None}, "inputs"),
            ({"scenario": SCENARIO_ID, "inputs": [CONFIGURED_VALUES]}, "inputs"),
            ({"scenario": SCENARIO_ID, "inputs": {"scenario": "other"}}, "'scenario'"),
        ):
            with self.subTest(request=request):
                status, _, body = self.post_json(request)

                self.assertEqual(status, 400)
                self.assertIn(expected, body["error"])

    def test_unsupported_scenario_is_rejected(self):
        for scenario in ("other-scenario", ["basic-agent-choice"], None):
            with self.subTest(scenario=scenario):
                status, _, body = self.post_json({"scenario": scenario, "inputs": {}})

                self.assertEqual(status, 400)
                self.assertIn("Unsupported scenario", body["error"])
                self.assertIn(repr(scenario), body["error"])

    def test_adapter_input_errors_return_the_adapter_error(self):
        for inputs in (
            {"action_values": {"coffee_a": 1}},
            {"action_values": {"coffee_a": "4", "coffee_b": 7, "coffee_c": 10}},
            {"unknown": 1},
        ):
            with self.subTest(inputs=inputs):
                with self.assertRaises((TypeError, ValueError)) as raised:
                    run({"scenario": SCENARIO_ID, **inputs})

                status, _, body = self.post_json({"scenario": SCENARIO_ID, "inputs": inputs})

                self.assertEqual(status, 400)
                self.assertEqual(body, {"error": str(raised.exception)})

    def test_out_of_range_values_return_a_json_400_and_the_server_stays_usable(self):
        # 10**400 is too large to convert to float.
        for value in (10**400, -1e300):
            with self.subTest(value=value):
                inputs = {"action_values": {**CONFIGURED_VALUES, "coffee_a": value}}

                status, _, body = self.post_json({"scenario": SCENARIO_ID, "inputs": inputs})

                self.assertEqual(status, 400)
                self.assertIn("out of range", body["error"])

        status, _, _ = self.post_json({"scenario": SCENARIO_ID, "inputs": {}})
        self.assertEqual(status, 200)

    def test_malformed_json_returns_a_json_error(self):
        for raw in (b"{not json", b"", b"\xff"):
            with self.subTest(raw=raw):
                status, _, body = self.send(raw)

                self.assertEqual(status, 400)
                self.assertIn("JSON", body["error"])

    def test_old_and_unknown_paths_return_a_json_404(self):
        for path in ("/basic-agent-choice", "/other", "/simulate/"):
            with self.subTest(path=path):
                status, _, body = self.post_json(
                    {"scenario": SCENARIO_ID, "inputs": {}}, path=path
                )

                self.assertEqual(status, 404)
                self.assertIn("/simulate", body["error"])

    def test_preflight_on_old_and_unknown_paths_returns_the_post_404(self):
        for path in ("/basic-agent-choice", "/other", "/simulate/"):
            with self.subTest(path=path):
                post_404 = self.post_json({"scenario": SCENARIO_ID, "inputs": {}}, path=path)
                status, _, body = self.send(None, method="OPTIONS", path=path)

                self.assertEqual(status, 404)
                self.assertEqual(body, post_404[2])

    def test_malformed_content_length_returns_a_json_400(self):
        for content_length in ("abc", "1.5", "1_0", "", "-1", "-100"):
            with self.subTest(content_length=content_length):
                status, body = self.post_headers_only(content_length)

                self.assertEqual(status, 400)
                self.assertIn("Content-Length", body["error"])

    def test_oversized_content_length_returns_a_json_413_without_reading(self):
        for content_length in (BODY_LIMIT + 1, 10 * 1024 * 1024):
            with self.subTest(content_length=content_length):
                status, body = self.post_headers_only(str(content_length))

                self.assertEqual(status, 413)
                self.assertIn(str(BODY_LIMIT), body["error"])

        # A body exactly at the limit is still read and parsed.
        status, _, body = self.send(b" " * BODY_LIMIT)
        self.assertEqual(status, 400)
        self.assertIn("JSON", body["error"])

    def test_content_length_beyond_int_conversion_limit_returns_a_json_413(self):
        # Longer than Python's default int-from-str digit limit (4300).
        too_many_digits = 5000

        for content_length in ("9" * too_many_digits, "0" * too_many_digits + "65537"):
            with self.subTest(digits=len(content_length)):
                status, body = self.post_headers_only(content_length)

                self.assertEqual(status, 413)
                self.assertIn(str(BODY_LIMIT), body["error"])

        # Leading zeros alone do not make a small length oversized.
        status, body = self.post_headers_only("0" * too_many_digits)
        self.assertEqual(status, 400)
        self.assertIn("JSON", body["error"])

    def test_incomplete_body_times_out_with_a_json_408(self):
        # Without a socket timeout a stalled client holds a server thread forever.
        self.assertEqual(SimulationHandler.timeout, 10)

        connection = HTTPConnection(self.host, self.port, timeout=5)

        try:
            connection.putrequest("POST", PATH)
            connection.putheader("Content-Type", "application/json")
            connection.putheader("Content-Length", "100")
            connection.endheaders(b'{"scenario"')
            response = connection.getresponse()
            status, body = response.status, json.loads(response.read())
        finally:
            connection.close()

        self.assertEqual(status, 408)
        self.assertIn("timed out", body["error"])

        status, _, _ = self.post_json({"scenario": SCENARIO_ID, "inputs": {}})
        self.assertEqual(status, 200)

    def test_repeated_content_length_returns_a_json_400_without_reading(self):
        for content_lengths in (("10", "0"), ("0", "10")):
            with self.subTest(content_lengths=content_lengths):
                status, body = self.post_headers_only(*content_lengths)

                self.assertEqual(status, 400)
                self.assertIn("Content-Length", body["error"])

    def assert_origin_allowed(self, origin, base_url):
        status, headers, _ = self.send(
            None, method="OPTIONS", origin=origin, base_url=base_url
        )

        self.assertEqual(status, 204)
        self.assertEqual(headers["Access-Control-Allow-Origin"], origin)
        self.assertEqual(headers["Vary"], "Origin")
        self.assertIn("POST", headers["Access-Control-Allow-Methods"])
        self.assertIn("Content-Type", headers["Access-Control-Allow-Headers"])

        _, headers, _ = self.send(
            json.dumps({"scenario": SCENARIO_ID, "inputs": {}}).encode(),
            origin=origin,
            base_url=base_url,
        )
        self.assertEqual(headers["Access-Control-Allow-Origin"], origin)

    def test_local_astro_origins_are_allowed(self):
        for base_url in (self.base_url, self.production_url):
            for origin in ALLOWED_ORIGINS:
                with self.subTest(origin=origin, base_url=base_url):
                    self.assert_origin_allowed(origin, base_url)

    def test_configured_production_origin_is_allowed(self):
        self.assert_origin_allowed(PRODUCTION_ORIGIN, self.production_url)

    def test_other_origins_are_not_allowed(self):
        for base_url, origin in (
            (self.base_url, "https://example.com"),
            (self.base_url, "http://localhost:3000"),
            # Without TER_ALLOWED_ORIGIN, the production origin is not allowed.
            (self.base_url, PRODUCTION_ORIGIN),
            (self.production_url, "https://example.com"),
            (self.production_url, "http://ter.example.org"),
            (self.production_url, "https://ter.example.org:8443"),
            (self.production_url, "https://ter.example.org.evil.com"),
            (self.production_url, "null"),
        ):
            with self.subTest(origin=origin, base_url=base_url):
                _, headers, _ = self.send(
                    None, method="OPTIONS", origin=origin, base_url=base_url
                )
                self.assertIsNone(headers["Access-Control-Allow-Origin"])

                _, headers, _ = self.send(
                    json.dumps({"scenario": SCENARIO_ID, "inputs": {}}).encode(),
                    origin=origin,
                    base_url=base_url,
                )
                self.assertIsNone(headers["Access-Control-Allow-Origin"])

    def test_no_production_origin_allows_only_the_local_origins(self):
        self.assertEqual(allowed_origins(None), set(ALLOWED_ORIGINS))
        self.assertEqual(SimulationHandler.cors_origins, set(ALLOWED_ORIGINS))

    def test_production_origin_must_be_one_exact_https_origin(self):
        self.assertEqual(
            allowed_origins(PRODUCTION_ORIGIN), {*ALLOWED_ORIGINS, PRODUCTION_ORIGIN}
        )
        self.assertIn(
            "https://ter.example.org:8443", allowed_origins("https://ter.example.org:8443")
        )

        for value in (
            "",
            "*",
            "https://*.example.org",
            "http://ter.example.org",
            "ter.example.org",
            "https://ter.example.org/",
            "https://ter.example.org/learn",
            "https://ter.example.org?x=1",
            "https://ter.example.org#top",
            "https://user:secret@ter.example.org",
            "https://ter.example.org:99999",
            "https://ter.example.org ",
            "https://Ter.Example.org",
            f"{PRODUCTION_ORIGIN},https://example.com",
        ):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "TER_ALLOWED_ORIGIN"):
                    allowed_origins(value)


if __name__ == "__main__":
    unittest.main()
