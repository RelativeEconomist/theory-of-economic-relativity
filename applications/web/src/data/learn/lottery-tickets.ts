/**
 * The three Lottery Tickets configurations as TER model rows. Text mirrors the
 * AgentSpecs in research/scenarios/lottery_tickets.py; if they disagree, the
 * executable code wins.
 */
import type { TerComponentMapping } from "./scenarios";

// No treatment badges: the actual chance is fixed, and M changes only
// through the disclosure checkbox.
type Row = Omit<TerComponentMapping, "mapping" | "testTreatment">;
type Key = TerComponentMapping["key"];

// Canonical names and definitions, in Model 5.1 order followed by realization.
const ROWS: Row[] = [
  { key: "G", symbol: "G", name: "Objective", definition: "Result or condition that provides the reference for valuation when valuation is used." },
  { key: "M", symbol: "M", name: "Model of reality", definition: "The agent's model of reality, including information, beliefs, assumptions, expectations, and interpretations." },
  { key: "F_hat", symbol: "F̂", name: "Perceived feasible set", definition: "Actions the agent perceives as available to attempt." },
  { key: "V", symbol: "V", name: "Valuation", definition: "Valuation of actions relative to the agent's objective." },
  { key: "H", symbol: "H", name: "Time horizon", definition: "Which future consequences the agent considers relevant to valuation." },
  { key: "D", symbol: "D", name: "Decision process", definition: "Process through which the agent selects among perceived feasible actions. It may condition directly on the model of reality and may use valuation when applicable." },
  { key: "C", symbol: "C", name: "Selected action", definition: "Action selected by the agent." },
  { key: "F", symbol: "F_t", name: "Objective feasible state of reality", definition: "The objectively realized conditions and constraints relevant when the selected action(s) at decision point t are realized. Not agent specific, and not an input to the decision process." },
  { key: "R", symbol: "R", name: "Reality function", definition: "Maps the selected action(s) and the relevant objectively realized state F_t to the realized outcome; its arguments depend on model scope." },
  { key: "O", symbol: "O", name: "Realized outcome", definition: "Realized outcome associated with the selected action." },
];

const SHARED: Partial<Record<Key, string>> = {
  F_hat: "Buy or skip. Skip only when the ticket costs more than his $50.",
  C: "Buy or skip, returned by the simulator.",
  F: "A one in a million chance, the ticket price and jackpot set in the simulator, and $50 available.",
  R: "Applies the actual chance, price, and jackpot to C.",
  O: "Win or lose the ticket’s net money, or $0 for skipping, shown with probabilities.",
};

const VALUE_MAXIMIZER: Partial<Record<Key, string>> = {
  H: "This draw only.",
  D: "Choose the option with the higher valuation. Skip if tied.",
};

const NOT_CONSULTED = "Not consulted by the routine.";

export const lotteryConfigurations = [
  {
    id: "alex_mistaken_odds",
    title: "Overestimates chances",
    reason: "He overestimates his chances",
    mappings: {
      ...SHARED,
      ...VALUE_MAXIMIZER,
      G: "Maximize expected money.",
      M: "Believes the chance of winning is 1 in 250,000, or 1 in 1,000,000 when told the actual chance.",
      V: "Buy: believed chance × jackpot − price. Skip: $0.",
    },
  },
  {
    id: "alex_entertainment_value",
    title: "Enjoys playing",
    reason: "He enjoys playing",
    mappings: {
      ...SHARED,
      ...VALUE_MAXIMIZER,
      G: "Maximize expected money plus enjoyment.",
      M: "Knows the actual chance of winning, 1 in 1,000,000.",
      V: "Buy: believed chance × jackpot + $15 enjoyment − price. Skip: $0.",
    },
  },
  {
    id: "alex_habit",
    title: "Follows a routine",
    reason: "He follows a routine",
    mappings: {
      ...SHARED,
      G: NOT_CONSULTED,
      M: "Knows the price. Believes the chance of winning is 1 in 250,000, or 1 in 1,000,000 when told the actual chance.",
      V: NOT_CONSULTED,
      H: NOT_CONSULTED,
      D: "Buy if the ticket is affordable and costs $30 or less. Otherwise skip.",
    },
  },
] satisfies { id: string; title: string; reason: string; mappings: Partial<Record<Key, string>> }[];

/** TER model rows for one configuration, for TerArchitecture. */
export const lotteryTerComponents = (id: string): TerComponentMapping[] => {
  const configuration = lotteryConfigurations.find((item) => item.id === id)!;
  return ROWS.map((row) => ({ ...row, mapping: configuration.mappings[row.key] ?? "" }));
};
