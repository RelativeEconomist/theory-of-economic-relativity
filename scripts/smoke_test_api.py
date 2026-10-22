"""
Smoke-test the deployed TER simulation API with a real simulation.

POSTs the fixed Feasible Set Learning scenario (Test 22) to API_URL +
/simulate and passes only if the response is HTTP 200 and equal to the
same adapter run locally from this checkout. Exits nonzero otherwise.

Run from the repository root:

    python3 scripts/smoke_test_api.py [API_URL]

API_URL defaults to https://api.theoryofeconomicrelativity.com.
"""

import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from research.adapters import feasible_set_learning  # noqa: E402

DEFAULT_API_URL = "https://api.theoryofeconomicrelativity.com"
ATTEMPTS = 5
RETRY_SECONDS = 10


def post_simulation(url: str) -> tuple[int, object]:
    """POST the Feasible Set Learning envelope and return (status, parsed body)."""
    body = json.dumps(
        {"scenario": feasible_set_learning.SCENARIO_ID, "inputs": {}}
    ).encode()
    request = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json", "User-Agent": "ter-release-smoke-test"},
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode(errors="replace")


def main() -> int:
    url = (sys.argv[1] if len(sys.argv) > 1 else DEFAULT_API_URL).rstrip("/") + "/simulate"

    # Round-trip through JSON so tuples compare equal to the lists the API returns.
    expected = json.loads(
        json.dumps(feasible_set_learning.run({"scenario": feasible_set_learning.SCENARIO_ID}))
    )

    # A fresh deployment can take a few seconds to serve, so retry before failing.
    for attempt in range(1, ATTEMPTS + 1):
        try:
            status, payload = post_simulation(url)
        except (OSError, ValueError) as error:
            status, payload = None, f"{type(error).__name__}: {error}"

        if status == 200 and payload == expected:
            selected = [period["selected_action"] for period in payload["periods"]]
            print(f"PASS {url}: {payload['scenario']} selected {selected}")
            return 0

        if status == 200:
            reason = "response differs from the local adapter run"
        else:
            reason = f"status {status}: {payload}"

        print(f"Attempt {attempt}/{ATTEMPTS} failed: {reason}", file=sys.stderr)

        if attempt < ATTEMPTS:
            time.sleep(RETRY_SECONDS)

    print(f"FAIL {url}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
