"""
Cloudflare Worker that serves the TER simulation endpoint in production.

POST /simulate takes and returns the same JSON as the local server
(applications.api.simulation). Only the transport differs:

- CORS allows exactly the TER_ALLOWED_ORIGIN origin, never localhost.
- A POST must declare its Content-Length, so the body size is known before
  it is read.
- Each client IP may POST 30 times a minute; preflights are not counted.
- The body must be UTF-8 JSON nested at most 32 levels deep; deeper nesting
  is refused before parsing.

Errors are {"error": "..."} with status 400 for a malformed Content-Length,
malformed or too deeply nested JSON, or a request the endpoint rejects; 404
for any other path; 405 for any other method; 411 for a missing
Content-Length; 413 for a body over 64 KiB; and 429 over the rate limit.

Configured and deployed through wrangler.api.jsonc at the repository root.
"""

import json
from urllib.parse import urlsplit

from workers import Response, WorkerEntrypoint

from applications.api.endpoint import MAX_BODY_BYTES, PATH, exact_https_origin, simulate

# The request envelope nests 3 levels: {"inputs": {"action_values": {...}}}.
# Parsing a few thousand levels overflows the Worker runtime's stack, which
# kills the isolate instead of raising, so nesting is bounded before parsing.
MAX_JSON_DEPTH = 32


def nests_deeper_than(text: str, max_depth: int) -> bool:
    """
    Return whether JSON text opens more than max_depth nested arrays and
    objects. Brackets and braces inside strings do not count.
    """
    depth = 0
    in_string = False
    escaped = False

    for character in text:
        if in_string:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
        elif character == '"':
            in_string = True
        elif character in "[{":
            depth += 1

            if depth > max_depth:
                return True
        elif character in "]}":
            depth -= 1

    return False


def json_response(status: int, payload: dict, headers: dict) -> Response:
    return Response(
        json.dumps(payload, allow_nan=False),
        status=status,
        headers={**headers, "Content-Type": "application/json"},
    )


async def read_json_body(request) -> tuple[int, object]:
    """
    Return (200, parsed JSON body), or (error status, {"error": ...}) when
    the body is undeclared, oversized, nested too deeply, or not JSON.
    """
    too_large = {"error": f"Request body must be at most {MAX_BODY_BYTES} bytes."}
    declared_length = request.headers.get("Content-Length")

    if declared_length is None:
        return 411, {"error": "Content-Length is required."}

    if not (declared_length.isascii() and declared_length.isdigit()):
        return 400, {"error": "Content-Length must be a single non-negative integer."}

    # Compare the digits as text so arbitrarily long values never reach
    # int(); equal-length decimal strings order like their numbers.
    digits = declared_length.lstrip("0") or "0"
    limit = str(MAX_BODY_BYTES)

    if (len(digits), digits) > (len(limit), limit):
        return 413, too_large

    body = await request.bytes()

    if len(body) > MAX_BODY_BYTES:
        return 413, too_large

    try:
        # Decode as UTF-8 first so the depth check scans the text json parses.
        text = body.decode()

        if nests_deeper_than(text, MAX_JSON_DEPTH):
            return 400, {
                "error": f"Request body must not nest JSON deeper than {MAX_JSON_DEPTH} levels."
            }

        return 200, json.loads(text)
    except ValueError:
        return 400, {"error": "Request body must be valid JSON."}


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        try:
            allowed_origin = exact_https_origin(self.env.TER_ALLOWED_ORIGIN)
        except ValueError as error:
            return json_response(500, {"error": f"Configuration error: {error}"}, {})

        cors_headers = {}

        if request.headers.get("Origin") == allowed_origin:
            cors_headers = {"Access-Control-Allow-Origin": allowed_origin, "Vary": "Origin"}

        if urlsplit(request.url).path != PATH:
            return json_response(
                404, {"error": f"Unknown path; POST to {PATH}."}, cors_headers
            )

        try:
            method = request.method
        except KeyError:
            # The Workers SDK raises for methods outside the standard HTTP set.
            method = None

        if method == "OPTIONS":
            return Response(
                None,
                status=204,
                headers={
                    **cors_headers,
                    "Access-Control-Allow-Methods": "POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type",
                },
            )

        if method != "POST":
            return json_response(
                405,
                {"error": f"Unsupported method; POST to {PATH}."},
                {**cors_headers, "Allow": "POST, OPTIONS"},
            )

        # Cloudflare sets CF-Connecting-IP itself, so a client cannot choose it.
        client_ip = request.headers.get("CF-Connecting-IP") or "unknown"
        rate_limit = await self.env.SIMULATE_RATE_LIMITER.limit(key=client_ip)

        if not rate_limit.success:
            return json_response(
                429, {"error": "Too many requests; try again in a minute."}, cors_headers
            )

        status, payload = await read_json_body(request)

        if status == 200:
            try:
                payload = simulate(payload)
            except (TypeError, ValueError) as error:
                status, payload = 400, {"error": str(error)}

        return json_response(status, payload, cors_headers)
