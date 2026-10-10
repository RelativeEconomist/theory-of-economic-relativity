#!/usr/bin/env bash
# Run the TER simulation API and the Astro dev server together; Ctrl+C stops both.
set -u

cd "$(dirname "$0")/.." || exit 1

api_pid=
web_pid=

# Signal and wait on only the services started here. Negative PIDs signal
# each service's whole process group (npm, Astro, Vite).
stop_services() {
  trap - INT TERM
  [ -n "$api_pid" ] && kill -- "-$api_pid"
  [ -n "$web_pid" ] && kill -- "-$web_pid"
  [ -n "$api_pid" ] && wait "$api_pid"
  [ -n "$web_pid" ] && wait "$web_pid"
} 2>/dev/null

trap 'stop_services; exit 130' INT
trap 'stop_services; exit 143' TERM

echo "Starting TER simulator (Ctrl+C stops both):"
echo "  API  http://127.0.0.1:8000"
echo "  Web  http://localhost:4321"

# Job control gives each service its own process group.
set -m
PYTHONDONTWRITEBYTECODE=1 python3.14 -m research.http.simulation </dev/null &
api_pid=$!
(cd applications/web && exec npm run dev) </dev/null &
web_pid=$!
set +m

wait "$api_pid" "$web_pid"
