/**
 * Posts a scenario's inputs to the Python `/simulate` endpoint
 * (research/http/endpoint.py) and returns its JSON result, or throws an
 * Error carrying the endpoint's message.
 */
const API_URL: string = import.meta.env.PUBLIC_TER_API_URL ?? "http://127.0.0.1:8000";
const ENDPOINT = `${API_URL.replace(/\/$/, "")}/simulate`;

export const runScenario = async <Result>(
  scenarioId: string,
  scenarioInputs: object,
): Promise<Result> => {
  let response: Response;
  try {
    response = await fetch(ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ scenario: scenarioId, inputs: scenarioInputs }),
    });
  } catch {
    throw new Error(`Could not reach the TER endpoint at ${ENDPOINT}.`);
  }

  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(body.error ?? `The TER endpoint returned status ${response.status}.`);
  }
  return body;
};
