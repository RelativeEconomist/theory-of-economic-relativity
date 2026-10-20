"""
Transport-neutral rules for the TER simulation endpoint.

The local server (research.http.simulation) and the Cloudflare Worker
(research.http.worker) share these, so both accept the same route, body
size, production origin form, and request envelope.
"""

import re

from research.adapters import asymmetric_information, basic_agent_choice, bounded_rationality

PATH = "/simulate"
MAX_BODY_BYTES = 64 * 1024

ADAPTERS = (basic_agent_choice, bounded_rationality, asymmetric_information)

ENVELOPE_KEYS = frozenset({"scenario", "inputs"})

# Lowercase https://host[:port] only: no wildcard, credentials, path, query,
# or fragment. Browsers send Origin in this form.
HTTPS_ORIGIN = re.compile(r"https://[a-z0-9-]+(\.[a-z0-9-]+)*(:(?P<port>[0-9]{1,5}))?")


def exact_https_origin(production_origin: str) -> str:
    """
    Return production_origin (the TER_ALLOWED_ORIGIN value) unchanged if it
    is one exact HTTPS origin; raise ValueError otherwise.
    """
    match = HTTPS_ORIGIN.fullmatch(production_origin)

    if not match or not 0 < int(match["port"] or 443) <= 65535:
        raise ValueError(
            "TER_ALLOWED_ORIGIN must be one exact lowercase HTTPS origin such as "
            "https://example.org (optional port; no path, query, fragment, "
            f"credentials, or wildcard); got {production_origin!r}."
        )

    return production_origin


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

    # Compare with ==, not a dict lookup, so unhashable values are rejected
    # as unsupported rather than raising.
    adapter = next((a for a in ADAPTERS if scenario == a.SCENARIO_ID), None)

    if adapter is None:
        supported = [a.SCENARIO_ID for a in ADAPTERS]
        raise ValueError(
            f"Unsupported scenario {scenario!r}; expected one of {supported}."
        )

    if not isinstance(inputs, dict):
        raise TypeError("inputs must be a JSON object.")

    if "scenario" in inputs:
        raise ValueError("inputs must not contain 'scenario'; set it at the top level.")

    return adapter.run({"scenario": scenario, **inputs})
