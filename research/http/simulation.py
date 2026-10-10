"""
Local HTTP endpoint that runs a TER scenario through its JSON-safe adapter.

POST /simulate with:

    {
        "scenario": "basic-agent-choice",
        "inputs": {"action_values": {"coffee_a": 4, "coffee_b": 7, "coffee_c": 10}},
    }

inputs may be empty; the adapter then runs the scenario's Python defaults.
The response is the adapter's JSON result, or {"error": "..."} with status
400 for a malformed or repeated Content-Length, malformed JSON, an invalid
envelope, an unsupported scenario, or inputs the adapter rejects; 408 when the
body stalls for 10 seconds; 413 for a body over 64 KiB; and
404 for any other path.

Run from the repository root for local development:

    python3 -m research.http.simulation

Browsers on the local Astro dev server (port 4321) may call it. Set
TER_ALLOWED_ORIGIN to one exact HTTPS origin to also allow a production site.
"""

import json
import os
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from research.adapters import basic_agent_choice

PATH = "/simulate"
HOST = "127.0.0.1"
PORT = 8000
LOCAL_ORIGINS = frozenset({"http://localhost:4321", "http://127.0.0.1:4321"})
MAX_BODY_BYTES = 64 * 1024
REQUEST_TIMEOUT_SECONDS = 10

ENVELOPE_KEYS = frozenset({"scenario", "inputs"})

# Lowercase https://host[:port] only: no wildcard, credentials, path, query,
# or fragment. Browsers send Origin in this form.
HTTPS_ORIGIN = re.compile(r"https://[a-z0-9-]+(\.[a-z0-9-]+)*(:(?P<port>[0-9]{1,5}))?")


def allowed_origins(production_origin: str | None) -> frozenset:
    """
    Return the exact origins allowed by CORS: the local Astro origins, plus
    production_origin (the TER_ALLOWED_ORIGIN value) when it is set.
    """
    if production_origin is None:
        return LOCAL_ORIGINS

    match = HTTPS_ORIGIN.fullmatch(production_origin)

    if not match or not 0 < int(match["port"] or 443) <= 65535:
        raise ValueError(
            "TER_ALLOWED_ORIGIN must be one exact lowercase HTTPS origin such as "
            "https://example.org (optional port; no path, query, fragment, "
            f"credentials, or wildcard); got {production_origin!r}."
        )

    return LOCAL_ORIGINS | {production_origin}


def simulate(request: dict) -> dict:
    """
    Validate a {"scenario", "inputs"} envelope and return the scenario
    adapter's result for {"scenario": ..., **inputs}.
    """
    if not isinstance(request, dict):
        raise TypeError("Request must be a JSON object with 'scenario' and 'inputs'.")

    missing = sorted(ENVELOPE_KEYS - set(request))
    unknown = sorted(set(request) - ENVELOPE_KEYS)

    if missing:
        raise ValueError(f"Missing request key(s): {missing}")

    if unknown:
        raise ValueError(f"Unknown request key(s): {unknown}")

    scenario, inputs = request["scenario"], request["inputs"]

    if scenario != basic_agent_choice.SCENARIO_ID:
        raise ValueError(
            f"Unsupported scenario {scenario!r}; "
            f"expected one of {[basic_agent_choice.SCENARIO_ID]}."
        )

    if not isinstance(inputs, dict):
        raise TypeError("inputs must be a JSON object.")

    if "scenario" in inputs:
        raise ValueError("inputs must not contain 'scenario'; set it at the top level.")

    return basic_agent_choice.run({"scenario": scenario, **inputs})


class SimulationHandler(BaseHTTPRequestHandler):
    # Socket timeout in seconds, so a stalled client cannot hold a thread.
    timeout = REQUEST_TIMEOUT_SECONDS
    cors_origins = LOCAL_ORIGINS

    def do_OPTIONS(self):
        """Answer the browser's CORS preflight for the POST below."""
        if self.path != PATH:
            self.send_json(404, {"error": f"Unknown path; POST to {PATH}."})
            return

        self.send_response(204)
        self.send_cors_headers()
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        if self.path != PATH:
            self.send_json(404, {"error": f"Unknown path; POST to {PATH}."})
            return

        # Check the declared length before reading so a bad header cannot
        # trigger a read-to-EOF or an oversized read.
        length_headers = self.headers.get_all("Content-Length", ["0"])

        if len(length_headers) != 1 or not (
            length_headers[0].isascii() and length_headers[0].isdigit()
        ):
            self.send_json(
                400, {"error": "Content-Length must be a single non-negative integer."}
            )
            return

        # Compare the digits as text so arbitrarily long values never reach
        # int(); equal-length decimal strings order like their numbers.
        digits = length_headers[0].lstrip("0") or "0"
        limit = str(MAX_BODY_BYTES)

        if (len(digits), digits) > (len(limit), limit):
            self.send_json(
                413, {"error": f"Request body must be at most {MAX_BODY_BYTES} bytes."}
            )
            return

        length = int(digits)

        try:
            request = json.loads(self.rfile.read(length))
        except TimeoutError:
            self.send_json(
                408, {"error": "Request timed out before the full body arrived."}
            )
            return
        except ValueError:
            self.send_json(400, {"error": "Request body must be valid JSON."})
            return

        try:
            result = simulate(request)
        except (TypeError, ValueError) as error:
            self.send_json(400, {"error": str(error)})
            return

        self.send_json(200, result)

    def send_cors_headers(self):
        origin = self.headers.get("Origin")

        if origin in self.cors_origins:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")

    def send_json(self, status, payload):
        body = json.dumps(payload, allow_nan=False).encode()

        self.send_response(status)
        self.send_cors_headers()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    # Fail before serving if TER_ALLOWED_ORIGIN is set but invalid.
    try:
        SimulationHandler.cors_origins = allowed_origins(
            os.environ.get("TER_ALLOWED_ORIGIN")
        )
    except ValueError as error:
        raise SystemExit(f"Configuration error: {error}")

    server = ThreadingHTTPServer((HOST, PORT), SimulationHandler)
    print(f"TER simulation endpoint: http://{HOST}:{PORT}{PATH}")
    server.serve_forever()
