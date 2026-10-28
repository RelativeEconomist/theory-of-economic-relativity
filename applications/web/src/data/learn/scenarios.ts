/**
 * Presentation metadata for the Learn hub.
 *
 * This file does not define or reinterpret TER. It only describes, for the
 * website, how a given executable scenario maps onto the existing TER
 * architecture. The canonical theory is theory/academic.md; the canonical
 * behavior of each scenario lives in its executable scenario module under
 * research/scenarios/ (e.g. basic_agent_choice.py) and/or its replication
 * test under research/tests/. If this file and that executable code ever
 * disagree, the executable code wins.
 */

/** One row of the core TER decision architecture, as it applies to a scenario. */
export interface TerComponentMapping {
  /** Stable identifier for the variable, independent of display formatting. */
  key: "G" | "M" | "F" | "F_hat" | "V" | "H" | "D" | "C" | "R" | "O";
  /** Display form of the symbol, e.g. "F̂" or "F_t" (rendered with a subscript). */
  symbol: string;
  /** Short name of the variable, e.g. "Perceived feasible set". */
  name: string;
  /** General TER definition of the variable (theory/academic.md). */
  definition: string;
  /** How this specific test configures, exercises, or holds this variable. */
  mapping: string;
  /** How the test treats this variable, e.g. "Fixed across agents". In the
   *  compact model view, "Not modeled" rows are listed after the variables. */
  testTreatment?: string;
}

export interface ScenarioField {
  label: string;
  value: string;
}

export interface Scenario {
  slug: string;
  /** Executable runner on the scenario page: "simulator" when the reader can
   *  adjust inputs, "simulation" when it runs a fixed specification. Omitted
   *  for documentation-only scenarios. */
  runner?: "simulator" | "simulation";
  title: string;
  category: string;
  summary: string;
  /** Display identifier for the source this scenario comes from, e.g. "Test 1"
   *  for a numbered replication test or "Model 5.2" for a named theory model.
   *  Rendered as-is; not assumed to be a numbered test. */
  sourceLabel?: string;
  economicQuestion?: string;
  /** One or two sentences for the page's Scenario section. Falls back to `summary`. */
  context?: string;
  /** Concrete description of how this test's market/agents are set up. */
  economicSetup?: string;
  /** Short statement of what varies across this test's cases vs. what is held fixed. */
  whatChanges?: string;
  /** Text for the page's Interpretation section. */
  interpretation?: string;
  /** Short TER-terms restatement of `whatChanges`, shown below it in Interpretation. */
  terNote?: string;
  terComponents?: TerComponentMapping[];
  /** One-sentence scope statement, shown in the page's Scenario section. */
  scope?: string;
  assumptions?: string[];
  hypotheses?: string[];
  configuration?: ScenarioField[];
  /** Python fields (label) and the TER variable each one specifies (value). */
  implementationMapping?: ScenarioField[];
  /** Simple label/value results. Use for tests with a single outcome to report. */
  results?: ScenarioField[];
  /** Comparison table across multiple cases. Use instead of `results` when a test's
   *  point is how the outcome differs across cases (e.g. different decision rules). */
  resultsTable?: { columns: string[]; rows: string[][] };
  /** Path to the executable test or scenario, relative to the repository root. */
  sourcePath?: string;
}

export const scenarios: Scenario[] = [
  {
    slug: "basic-agent-choice",
    runner: "simulator",
    title: "Basic Agent Choice",
    category: "Individual choice",
    summary:
      "A single agent chooses its highest-valued action among three coffees it perceives as available.",
    sourceLabel: "Test 1",
    economicQuestion: "Given multiple coffee options, which one will an agent choose?",
    context:
      "An agent chooses among three coffees, each with a different assigned value. The agent considers all three options and uses a decision process that selects the coffee with the highest value.",
    terComponents: [
      {
        key: "G",
        symbol: "G",
        name: "Objective",
        definition: "Result or condition that provides the reference for valuation when valuation is used.",
        mapping: "Choose coffee.",
        testTreatment: "Fixed",
      },
      {
        key: "M",
        symbol: "M",
        name: "Model of reality",
        definition:
          "The agent's model of reality, including information, beliefs, assumptions, expectations, and interpretations.",
        mapping: "Left empty: neither V nor D uses information or beliefs.",
        testTreatment: "Fixed",
      },
      {
        key: "F",
        symbol: "F_t",
        name: "Objective feasible state of reality",
        definition:
          "The objectively realized conditions and constraints relevant when the selected action(s) at decision point t are realized. Not agent specific, and not an input to the decision process.",
        mapping: "Not modeled: no action is realized.",
        testTreatment: "Not modeled",
      },
      {
        key: "F_hat",
        symbol: "F̂",
        name: "Perceived feasible set",
        definition: "Actions the agent perceives as available to attempt.",
        mapping: "All three coffees.",
        testTreatment: "Fixed",
      },
      {
        key: "V",
        symbol: "V",
        name: "Valuation",
        definition: "Valuation of actions relative to the agent's objective.",
        mapping: "A value for each coffee, set in the simulator.",
        testTreatment: "Editable",
      },
      {
        key: "H",
        symbol: "H",
        name: "Time horizon",
        definition: "Which future consequences the agent considers relevant to valuation.",
        mapping: "Current decision.",
        testTreatment: "Fixed",
      },
      {
        key: "D",
        symbol: "D",
        name: "Decision process",
        definition:
          "Process through which the agent selects among perceived feasible actions. It may condition directly on the model of reality and may use valuation when applicable.",
        mapping: "Select the coffee with the highest value.",
        testTreatment: "Fixed",
      },
      {
        key: "C",
        symbol: "C",
        name: "Selected action",
        definition: "Action selected by the agent.",
        mapping: "The coffee D selects, returned by the simulator.",
        testTreatment: "Output",
      },
      {
        key: "R",
        symbol: "R",
        name: "Reality function",
        definition:
          "Maps the selected action(s) and the relevant objectively realized state F_t to the realized outcome; its arguments depend on model scope.",
        mapping: "Not modeled: no action is realized.",
        testTreatment: "Not modeled",
      },
      {
        key: "O",
        symbol: "O",
        name: "Realized outcome",
        definition: "Realized outcome associated with the selected action.",
        mapping: "Not modeled: the scenario ends at the selected action.",
        testTreatment: "Not modeled",
      },
    ],
    scope: "One agent, one decision. This illustrates TER Model 5.1, not real coffee demand.",
    assumptions: [
      "Values are hand-assigned for each run, not derived from any utility function.",
      "Ties go to the first tied coffee in F̂ order: Coffee A, Coffee C, Coffee B.",
    ],
    interpretation:
      "Changing how the agent values each coffee can change which one it selects. In this example, the decision process always chooses the highest-valued option, although TER does not require every agent to make decisions this way.",
    hypotheses: [
      "The agent selects the highest-valued action in its perceived feasible set.",
    ],
    implementationMapping: [
      { label: "objective", value: "G" },
      { label: "model_of_reality", value: "M (empty)" },
      { label: "perceived_feasible_set", value: "F̂" },
      { label: "valuation, read by mapped_value", value: "V" },
      { label: "horizon", value: "H" },
      { label: "decision_process = maximize_value", value: "D" },
      { label: "selected_action", value: "C" },
    ],
    sourcePath: "research/scenarios/basic_agent_choice.py",
  },
  {
    slug: "bounded-rationality",
    runner: "simulator",
    title: "Bounded Rationality",
    category: "Individual choice",
    summary:
      "The same coffee buyer picks a different coffee once its decision process only searches part of its perceived feasible set — TER does not require universal optimization.",
    sourceLabel: "Test 3",
    economicQuestion:
      "When an agent has several coffee options, how might limiting its search affect which one it chooses?",
    context:
      "An agent chooses among three coffees with different values. It can either consider every option or limit its search to the first few coffees in a specified order. By comparing these two decision processes, we can see how searching fewer options may change the choice.",
    terComponents: [
      {
        key: "G",
        symbol: "G",
        name: "Objective",
        definition: "Result or condition that provides the reference for valuation when valuation is used.",
        mapping: "Choose preferred coffee.",
        testTreatment: "Fixed",
      },
      {
        key: "M",
        symbol: "M",
        name: "Model of reality",
        definition:
          "The agent's model of reality, including information, beliefs, assumptions, expectations, and interpretations.",
        mapping: "Left empty: neither V nor D uses information or beliefs.",
        testTreatment: "Fixed",
      },
      {
        key: "F",
        symbol: "F_t",
        name: "Objective feasible state of reality",
        definition:
          "The objectively realized conditions and constraints relevant when the selected action(s) at decision point t are realized. Not agent specific, and not an input to the decision process.",
        mapping: "Not modeled: no action is realized.",
        testTreatment: "Not modeled",
      },
      {
        key: "F_hat",
        symbol: "F̂",
        name: "Perceived feasible set",
        definition: "Actions the agent perceives as available to attempt.",
        mapping: "All three coffees, in the same order, under both decision processes.",
        testTreatment: "Fixed",
      },
      {
        key: "V",
        symbol: "V",
        name: "Valuation",
        definition: "Valuation of actions relative to the agent's objective.",
        mapping: "A value for each coffee, set in the simulator.",
        testTreatment: "Editable",
      },
      {
        key: "H",
        symbol: "H",
        name: "Time horizon",
        definition: "Which future consequences the agent considers relevant to valuation.",
        mapping: "Current purchase.",
        testTreatment: "Fixed",
      },
      {
        key: "D",
        symbol: "D",
        name: "Decision process",
        definition:
          "Process through which the agent selects among perceived feasible actions. It may condition directly on the model of reality and may use valuation when applicable.",
        mapping:
          "Maximize value checks every coffee; limited search checks only the first few in its search order. Each selects the highest value among the coffees it checks.",
        testTreatment: "Editable",
      },
      {
        key: "C",
        symbol: "C",
        name: "Selected action",
        definition: "Action selected by the agent.",
        mapping: "The coffee D selects, returned by the simulator.",
        testTreatment: "Output",
      },
      {
        key: "R",
        symbol: "R",
        name: "Reality function",
        definition:
          "Maps the selected action(s) and the relevant objectively realized state F_t to the realized outcome; its arguments depend on model scope.",
        mapping: "Not modeled: no action is realized.",
        testTreatment: "Not modeled",
      },
      {
        key: "O",
        symbol: "O",
        name: "Realized outcome",
        definition: "Realized outcome associated with the selected action.",
        mapping: "Not modeled: the scenario ends at the selected action.",
        testTreatment: "Not modeled",
      },
    ],
    scope: "One agent, one decision. This illustrates TER Model 5.1, not real coffee demand.",
    assumptions: [
      "Values are hand-assigned for each run, not derived from any utility function.",
      "Search limit and search order configure limited search. They are not TER primitives and do not change F̂.",
      "Ties go to the first tied coffee checked: in F̂ order (Nearby, Office, Best) under maximize value, in search order under limited search.",
    ],
    whatChanges:
      "An agent that considers every coffee selects the highest-valued option. When its search is limited, it may select a lower-valued coffee without ever evaluating the best one. Searching more options or changing their search order can change the result.",
    terNote: "Limited search is one D specification; TER does not require optimization.",
    hypotheses: [
      "Exhaustive search selects the highest-valued action.",
      "Limited search can select a lower-valued action.",
      "Increasing search depth can change the selected action.",
      "Search order can matter under incomplete search.",
    ],
    implementationMapping: [
      { label: "objective", value: "G" },
      { label: "model_of_reality", value: "M (empty)" },
      { label: "perceived_feasible_set", value: "F̂" },
      { label: "valuation, read by mapped_value", value: "V" },
      { label: "horizon", value: "H" },
      { label: "decision_process = maximize_value or limited_search", value: "D" },
      { label: "decision_parameters: search_limit, search_order", value: "D configuration" },
      { label: "selected_action", value: "C" },
    ],
    resultsTable: {
      columns: ["Case", "How much is searched", "Selected action"],
      rows: [
        ["Exhaustive search", "All options", "Best Coffee (10)"],
        ["Limited search", "First 2", "Office Coffee (7)"],
        ["Broader search", "First 3", "Best Coffee (10)"],
        ["Reordered limited search", "First 2 in new order", "Best Coffee (10)"],
      ],
    },
    sourcePath: "research/scenarios/bounded_rationality.py",
  },
  {
    slug: "pokemon-card-choice",
    title: "Pokémon: Trade or sell?",
    sourceLabel: "Trade or sell?",
    category: "Individual choice",
    summary: "Would you complete your collection or try to sell for more?",
  },
  {
    slug: "supply-and-demand",
    title: "Supply and Demand",
    category: "Markets",
    summary:
      "Independent buyer and seller decisions aggregate into demand, supply, and a market-clearing price.",
    sourceLabel: "Test 7",
    economicQuestion:
      "How do individual decisions by buyers and sellers determine supply, demand, and the price at which a market clears?",
    economicSetup:
      "A market contains five buyers and five sellers, each with different willingness-to-pay values or selling costs. At different prices, buyers decide whether to purchase and sellers decide whether to sell. By comparing their choices, the test identifies the price at which the quantity buyers want equals the quantity sellers offer.",
    whatChanges:
      "As prices rise, fewer buyers are willing to purchase and more sellers are willing to sell. The test identifies a market-clearing price of 5, then demonstrates how adding a buyer or seller can change that price. It compares decisions across possible prices rather than simulating how prices adjust over time.",
    terComponents: [
      {
        key: "G",
        symbol: "G",
        name: "Objective",
        definition: "Result or condition that provides the reference for valuation when valuation is used.",
        mapping: "Every buyer and seller pursues \"maximize transaction value.\"",
        testTreatment: "Fixed across agents",
      },
      {
        key: "M",
        symbol: "M",
        name: "Model of reality",
        definition:
          "The agent's model of reality, including information, beliefs, assumptions, expectations, and interpretations.",
        mapping:
          "Agents evaluate their choices using the quoted candidate market price for that case. The test checks candidate prices ranging from 1 through 9.",
        testTreatment: "Price varies",
      },
      {
        key: "F",
        symbol: "F_t",
        name: "Objective feasible state of reality",
        definition:
          "The objectively realized conditions and constraints relevant when the selected action(s) at decision point t are realized. Not agent specific, and not an input to the decision process.",
        mapping: "F_t and outcome realization are outside this scenario's scope.",
        testTreatment: "Outside scope",
      },
      {
        key: "F_hat",
        symbol: "F̂",
        name: "Perceived feasible set",
        definition: "Actions the agent perceives as available to attempt.",
        mapping:
          "Buyers perceive buying and not buying as available; sellers perceive selling and not selling as available.",
        testTreatment: "Fixed",
      },
      {
        key: "V",
        symbol: "V",
        name: "Valuation",
        definition: "Valuation of actions relative to the agent's objective.",
        mapping:
          "Buyers value buying according to the difference between their reservation value and the quoted price. Sellers value selling according to the difference between the quoted price and their cost. Because reservation values and costs differ across agents, the same price can lead different agents to make different choices.",
        testTreatment: "Varies across agents and prices",
      },
      {
        key: "H",
        symbol: "H",
        name: "Time horizon",
        definition: "Which future consequences the agent considers relevant to valuation.",
        mapping: "\"current transaction\"",
        testTreatment: "Fixed",
      },
      {
        key: "D",
        symbol: "D",
        name: "Decision process",
        definition: "Process through which the agent selects among perceived feasible actions. It may condition directly on the model of reality and may use valuation when applicable.",
        mapping:
          "Each buyer compares buying with not buying, and each seller compares selling with not selling. The action with the higher value is selected. If the two actions have equal value, the test is configured so the agent transacts.",
        testTreatment: "Fixed",
      },
      {
        key: "C",
        symbol: "C",
        name: "Selected action",
        definition: "Action selected by the agent.",
        mapping: "Each buyer selects buy or not buy; each seller selects sell or not sell.",
        testTreatment: "Endogenously selected",
      },
      {
        key: "O",
        symbol: "O",
        name: "Realized outcome",
        definition: "Realized outcome associated with the selected action.",
        mapping:
          "No realized outcome is modeled. The test counts the buyers' and sellers' selected actions at each candidate price to get quantity demanded, quantity supplied, and excess demand. This counting is a test-specific analysis, not R, and its results are not a TER outcome. A candidate price clears the market when quantity demanded equals quantity supplied.",
        testTreatment: "Not modeled; test-specific counting",
      },
    ],
    assumptions: [
      "Market clearing is found by evaluating decentralized buyer and seller decisions across a fixed set of candidate prices.",
      "The test does not model a continuous auction or an endogenous price-adjustment process. It identifies the price at which quantity demanded and quantity supplied are equal.",
      "When transacting and not transacting have equal value, the agent transacts. This means zero-surplus buyers and sellers participate.",
    ],
    hypotheses: [
      "Quantity demanded falls as price rises.",
      "Quantity supplied rises as price rises.",
      "The baseline market has a clearing price.",
      "Increased demand raises the clearing price.",
      "Increased supply lowers the clearing price.",
      "The test-specific counting of independently selected actions gives quantity demanded, quantity supplied, and a market-clearing state over the specified price grid.",
      "Excess demand is positive below the clearing price, zero at the clearing price, and negative above it.",
    ],
    configuration: [
      { label: "Candidate prices", value: "1–9" },
      { label: "Buyer reservation values", value: "9, 8, 7, 6, 5" },
      { label: "Seller costs", value: "1, 2, 3, 4, 5" },
      { label: "Buyer choices", value: "Buy or do not buy" },
      { label: "Seller choices", value: "Sell or do not sell" },
      { label: "Objective", value: "Maximize transaction value" },
      { label: "Time horizon", value: "Current transaction" },
    ],
    results: [
      {
        label: "Baseline market",
        value: "Clearing price: 5\nQuantity demanded: 5\nQuantity supplied: 5",
      },
      {
        label: "Increased demand",
        value: "Adding a buyer with reservation value 10 raises the clearing price from 5 to 6.",
      },
      {
        label: "Increased supply",
        value: "Adding a seller with cost 4 lowers the clearing price from 5 to 4.",
      },
    ],
    resultsTable: {
      columns: ["Candidate price", "Excess demand"],
      rows: [
        ["4", "Positive"],
        ["5", "Zero — market clears"],
        ["6", "Negative"],
      ],
    },
    sourcePath: "research/tests/test_07_supply_and_demand.py",
  },
  {
    slug: "asymmetric-information",
    runner: "simulator",
    title: "Asymmetric Information",
    category: "Information",
    summary:
      "High-quality sellers withdraw when individual quality cannot be observed and the market prices goods using pooled expected quality.",
    sourceLabel: "Test 4",
    economicQuestion:
      "When buyers cannot tell whether a used car is high or low quality, how does that affect which cars sellers are willing to sell?",
    context:
      "Six sellers each own a used car and know its quality. When buyers cannot observe the quality of individual cars, every seller receives the same price based on expected quality. The test compares this situation with one where each car's quality can be verified and priced separately.",
    scope:
      "One decision point, six interacting sellers. This illustrates TER Models 5.1 and 5.3, not real used-car markets.",
    economicSetup:
      "The market contains three high-quality sellers and three low-quality sellers. High-quality goods are worth 10, and their sellers have a reservation value of 8. Low-quality goods are worth 4, and their sellers have a reservation value of 2. The market initially believes that 50% of the goods for sale are high quality. Every seller chooses between selling at the offered price and holding onto the good.",
    whatChanges:
      "When every car receives the same pooled price, high-quality sellers may find that selling is no longer worthwhile. In this example, only low-quality cars are sold under pooled pricing. When individual quality can be verified, all six sellers choose to sell. This demonstrates the adverse-selection mechanism in Akerlof's market for lemons.",
    terNote:
      "In TER terms, only each seller's M (the price it observes) changes; G, F̂, V, H, D, and F_t stay fixed. All six selected actions meet the same F_t through one joint R, which produces the system outcome O_t. No seller-level outcome is defined, so O_t is not a sum of individual outcomes.",
    terComponents: [
      {
        key: "G",
        symbol: "G",
        name: "Objective",
        definition: "Result or condition that provides the reference for valuation when valuation is used.",
        mapping: "Every seller's objective is \"maximize value from the sale decision.\"",
        testTreatment: "Fixed",
      },
      {
        key: "M",
        symbol: "M",
        name: "Model of reality",
        definition:
          "The agent's model of reality, including information, beliefs, assumptions, expectations, and interpretations.",
        mapping:
          "Each seller's model holds the offered price it observes and its belief about its own car's quality. The reality rule reads neither. The observed price is what changes between the two cases: the pooled price under asymmetric information, or the seller's own true-quality price under verified pricing. Set in the simulator.",
        testTreatment: "Editable",
      },
      {
        key: "F",
        symbol: "F_t",
        name: "Objective feasible state of reality",
        definition:
          "The objectively realized conditions and constraints relevant when the selected action(s) at decision point t are realized. Not agent specific, and not an input to the decision process.",
        mapping:
          "The reality rule reads each car's actual quality, a scenario-specified condition that represents one relevant aspect of F_t. It is not a complete representation of F_t.",
        testTreatment: "Fixed",
      },
      {
        key: "F_hat",
        symbol: "F̂",
        name: "Perceived feasible set",
        definition: "Actions the agent perceives as available to attempt.",
        mapping:
          "Every seller perceives both selling and holding as available.",
        testTreatment: "Fixed",
      },
      {
        key: "V",
        symbol: "V",
        name: "Valuation",
        definition: "Valuation of actions relative to the agent's objective.",
        mapping:
          "A seller values selling as the offered price it observes (from its model of reality) minus its reservation value, which represents the opportunity cost of giving up the good.",
        testTreatment: "Fixed",
      },
      {
        key: "H",
        symbol: "H",
        name: "Time horizon",
        definition: "Which future consequences the agent considers relevant to valuation.",
        mapping: "\"current sale decision\"",
        testTreatment: "Fixed",
      },
      {
        key: "D",
        symbol: "D",
        name: "Decision process",
        definition:
          "Process through which the agent selects among perceived feasible actions. It may condition directly on the model of reality and may use valuation when applicable.",
        mapping:
          "Each seller compares selling with holding and selects the higher-valued option.",
        testTreatment: "Fixed",
      },
      {
        key: "C",
        symbol: "C",
        name: "Selected action",
        definition: "Action selected by the agent.",
        mapping: "Each seller selects either sell or hold, returned by the simulator.",
        testTreatment: "Output",
      },
      {
        key: "R",
        symbol: "R",
        name: "Reality function",
        definition:
          "Maps the selected action(s) and the relevant objectively realized state F_t to the realized outcome; its arguments depend on model scope.",
        mapping:
          "One joint rule takes every seller's selected action together, with each car's actual quality, and counts the cars sold by actual quality. It never reads a seller's model of reality.",
        testTreatment: "Fixed",
      },
      {
        key: "O",
        symbol: "O_t",
        name: "System outcome",
        definition: "Realized system outcome produced by interacting selected actions encountering F_t.",
        mapping:
          "How many high-quality and low-quality cars are sold, and the total, returned by the simulator. No seller-level outcomes O_{i,t} are defined.",
        testTreatment: "Output",
      },
    ],
    assumptions: [
      "Buyers are not represented as individual TER agents in this test. The price each seller is offered is information the seller observes when deciding, so it is held in the seller's model of reality (M), not computed by a separate buyer agent or rule. Each seller is assumed to observe its offered price correctly.",
      "Under pooled pricing, every seller observes the same population-level price (based on the believed share of high-quality goods) — the same price regardless of the seller's own quality. The simulator can change that believed share; actual quality stays 3 high, 3 low, and R never reads the believed share.",
      "Under verified pricing, each seller instead observes its own true price, so a seller's quality determines the price it faces.",
      "Both prices are fixed scenario data, set directly in each seller's initial model of reality — not TER feedback, since neither price depends on a realized outcome.",
      "Sellers are assumed to know their own quality perfectly. TER does not require this.",
      "Divergence between F̂ and what reality permits is not modeled in this test.",
    ],
    hypotheses: [
      "Under pooled, asymmetric-information pricing, high-quality sellers withhold their goods from the market.",
      "Under pooled pricing, low-quality sellers still sell.",
      "This produces adverse selection: only low-quality goods trade under pooled pricing.",
      "Under verified, symmetric-information pricing, both high-quality and low-quality goods trade.",
      "The same sellers, with the same reservation values and perceived feasible sets, decide differently when the offered price changes from the pooled price to the verified price.",
      "Gains from trade exist for high-quality sellers, but go unrealized under asymmetric information.",
    ],
    configuration: [
      { label: "Sellers", value: "3 high-quality, 3 low-quality" },
      { label: "High-quality good value / seller reservation value", value: "10 / 8" },
      { label: "Low-quality good value / seller reservation value", value: "4 / 2" },
      { label: "Believed high-quality share (pooled case)", value: "50%" },
      { label: "Actions", value: "Sell, hold" },
      { label: "Valuation method", value: "Offered price minus reservation value" },
      { label: "Time horizon", value: "Current sale decision" },
    ],
    implementationMapping: [
      { label: "objective", value: "G" },
      { label: "model_of_reality: known_quality, price", value: "M" },
      { label: "parameters[\"actual_quality_by_seller\"]", value: "Aspect of F_t, read only by R" },
      { label: "perceived_feasible_set", value: "F̂" },
      { label: "valuation, read by price_taking_value", value: "V" },
      { label: "horizon", value: "H" },
      { label: "decision_process = maximize_value", value: "D" },
      { label: "selected_action", value: "C" },
      { label: "reality = quality_market_reality", value: "R" },
      { label: "trace[t].reality.system", value: "O_t" },
    ],
    results: [
      {
        label: "Why high-quality sellers withhold",
        value:
          "With a 50% believed share of high-quality goods, the pooled price is 7. High-quality sellers require 8 to sell, so they hold. Low-quality sellers require only 2, so they sell. The market therefore ends up trading only low-quality goods.",
      },
      {
        label: "Gains from trade",
        value:
          "High-quality goods have value 10 and seller reservation value 8, so gains from trade exist, but those trades go unrealized under pooled asymmetric-information pricing.",
      },
    ],
    resultsTable: {
      columns: ["Metric", "Pooled pricing (asymmetric information)", "Verified pricing (symmetric information)"],
      rows: [
        ["Information used to set price", "Believed share: 50% high quality", "Each seller's own true quality"],
        ["Price offered to high-quality sellers", "7", "10"],
        ["Price offered to low-quality sellers", "7", "4"],
        ["High-quality sellers sold", "0 of 3", "3 of 3"],
        ["Low-quality sellers sold", "3 of 3", "3 of 3"],
        ["Total sold", "3", "6"],
      ],
    },
    sourcePath: "research/scenarios/asymmetric_information.py",
  },
  {
    slug: "externalities",
    title: "Externalities",
    category: "Externalities",
    summary:
      "A privately profitable action can create a negative external effect and produce lower total value under a specified social-value measure.",
    sourceLabel: "Test 8",
    economicQuestion:
      "Can a decision that benefits a business also create costs for others, and can accounting for those costs change the decision?",
    economicSetup:
      "A firm decides whether to produce a good. Producing gives the firm a private value of 4 but creates an external cost of 7 for others. The test compares what the firm chooses when it considers only its private benefit with what it chooses when that external cost is included in its valuation.",
    whatChanges:
      "When the firm considers only its own benefit, it chooses to produce. However, the production decision generates a net value of −3 under the test's specified social-value measure. When the firm includes the external cost in its valuation, it chooses not to produce. The test does not model how that internalization would occur in practice.",
    terComponents: [
      {
        key: "G",
        symbol: "G",
        name: "Objective",
        definition: "Result or condition that provides the reference for valuation when valuation is used.",
        mapping: "The firm's objective is \"maximize value from the production decision.\"",
        testTreatment: "Fixed",
      },
      {
        key: "M",
        symbol: "M",
        name: "Model of reality",
        definition:
          "The agent's model of reality, including information, beliefs, assumptions, expectations, and interpretations.",
        mapping:
          "The firm's model holds its belief about each action's external effect, the same in both scenarios. By assumption it matches the scenario's actual external effects. The test does not change it.",
        testTreatment: "Fixed",
      },
      {
        key: "F",
        symbol: "F_t",
        name: "Objective feasible state of reality",
        definition:
          "The objectively realized conditions and constraints relevant when the selected action(s) at decision point t are realized. Not agent specific, and not an input to the decision process.",
        mapping:
          "The reality rule reads the scenario's actual private values and external effects for each action. These are scenario-specified conditions that represent relevant aspects of F_t, not a complete representation of it.",
        testTreatment: "Fixed",
      },
      {
        key: "F_hat",
        symbol: "F̂",
        name: "Perceived feasible set",
        definition: "Actions the agent perceives as available to attempt.",
        mapping: "The firm perceives both actions as available.",
        testTreatment: "Fixed",
      },
      {
        key: "V",
        symbol: "V",
        name: "Valuation",
        definition: "Valuation of actions relative to the agent's objective.",
        mapping:
          "The only TER input that changes between the two cases. Private-incentive valuation counts only the firm's own gain; internalized valuation adds the external effect on top of that same gain. Both read the same underlying private-value and external-effect facts — only how they're combined differs.",
        testTreatment: "Varied across cases",
      },
      {
        key: "H",
        symbol: "H",
        name: "Time horizon",
        definition: "Which future consequences the agent considers relevant to valuation.",
        mapping: "\"current production decision\"",
        testTreatment: "Fixed",
      },
      {
        key: "D",
        symbol: "D",
        name: "Decision process",
        definition:
          "Process through which the agent selects among perceived feasible actions. It may condition directly on the model of reality and may use valuation when applicable.",
        mapping:
          "The firm compares all perceived feasible actions and selects the one with the highest value.",
        testTreatment: "Fixed",
      },
      {
        key: "C",
        symbol: "C",
        name: "Selected action",
        definition: "Action selected by the agent.",
        mapping:
          "Produce in the private-incentive case; do not produce in the internalized case.",
        testTreatment: "Endogenously selected",
      },
      {
        key: "O",
        symbol: "O",
        name: "Realized outcome",
        definition: "Realized outcome associated with the selected action.",
        mapping:
          "The reality rule takes the selected action and the scenario's own private-value and external-effect data and reports O_{i,t}: the private value, the external effect, and this test's specified social value, defined here as private value plus external effect. This is a single-agent specification, so no system outcome O_t is defined.",
        testTreatment: "Result",
      },
    ],
    assumptions: [
      "The external effect is represented as a test-specific scalar attached to each action.",
      "This is a single-agent test. There is no second TER agent representing society or the party bearing the external cost.",
      "The social-value measure used in this test is private value plus external effect. This measure is test-specific, not a universal TER welfare rule.",
      "Internalization is represented only by changing the firm's valuation rule over the same facts.",
      "The test does not model how internalization occurs in reality. No tax, regulation, liability rule, bargaining process, or equilibrium mechanism is simulated.",
    ],
    hypotheses: [
      "Producing is privately profitable.",
      "Producing creates a negative external effect.",
      "Private value can be positive while the specified social value is negative.",
      "The privately selected action can have lower specified social value than the available alternative.",
      "Including the external effect in the firm's own valuation can change the selected action.",
    ],
    configuration: [
      { label: "Agent", value: "1 firm" },
      { label: "Actions", value: "Produce, do not produce" },
      { label: "Private value of producing", value: "4" },
      { label: "External effect of producing", value: "−7" },
      { label: "Private value of not producing", value: "0" },
      { label: "External effect of not producing", value: "0" },
      {
        label: "Decision process",
        value: "Compare all perceived options and choose the highest-valued one",
      },
      { label: "Time horizon", value: "Current production decision" },
    ],
    results: [
      {
        label: "Why the selected action changes",
        value:
          "Producing gives the firm private value 4, so it chooses to produce when it ignores the external effect. But producing also creates an external effect of −7, giving a specified social value of −3. When that external effect is included in the firm's own valuation, producing is valued at −3 and the firm instead chooses not to produce, which has value 0.",
      },
    ],
    resultsTable: {
      columns: ["Metric", "Private incentive", "Externality internalized"],
      rows: [
        ["Firm's valuation of producing", "4", "−3"],
        ["Firm's valuation of not producing", "0", "0"],
        ["Selected action", "Produce", "Do not produce"],
      ],
    },
    sourcePath: "research/tests/test_08_externalities.py",
  },
  {
    slug: "actual-vs-perceived-feasibility",
    title: "Perceived Feasibility vs. Scenario Permission",
    category: "Feasibility",
    summary:
      "A producer may select an action the scenario does not permit. The selected action stays the one the decision process chose; the realized outcome shows what the scenario allowed.",
    sourceLabel: "Model 5.2",
    economicQuestion:
      "What happens when an agent believes it can take an action, but reality does not allow that action to be fully carried out?",
    economicSetup:
      "Three producers choose how much to produce: nothing, 60 units, or 100 units. Although they use the same values and decision process, they differ in which actions they perceive as available and what the scenario actually permits. The test compares what each producer selects with what is ultimately realized.",
    whatChanges:
      "A producer may choose to produce 100 units even when reality does not permit that amount. Under this test's realization rule, the decision remains unchanged, but actual production can be limited to 60 units or even zero. This illustrates why TER distinguishes an agent's selected action from its realized outcome.",
    terComponents: [
      {
        key: "G",
        symbol: "G",
        name: "Objective",
        definition: "Result or condition that provides the reference for valuation when valuation is used.",
        mapping: "Every producer seeks to maximize realized production value.",
        testTreatment: "Fixed",
      },
      {
        key: "M",
        symbol: "M",
        name: "Model of reality",
        definition:
          "The agent's model of reality, including information, beliefs, assumptions, expectations, and interpretations.",
        mapping:
          "No distinct information, belief, or expectation is varied across producers in this test.",
        testTreatment: "Fixed",
      },
      {
        key: "F",
        symbol: "F_t",
        name: "Objective feasible state of reality",
        definition:
          "The objectively realized conditions and constraints relevant when the selected action(s) at decision point t are realized. Not agent specific, and not an input to the decision process.",
        mapping:
          "The scenario's permission data lists the permitted actions for each producer: hold or produce 60 for the accurate and mistaken producers, hold only for the severely mismatched producer. This data represents the relevant constraint (a production ceiling) in this implementation; it is not F_t itself. It is indexed by producer for convenience, but F_t is not agent specific, and only the reality rule reads it.",
        testTreatment: "Fixed; permission data differs by producer",
      },
      {
        key: "F_hat",
        symbol: "F̂",
        name: "Perceived feasible set",
        definition: "Actions the agent perceives as available to attempt.",
        mapping:
          "The accurate producer perceives exactly the permitted actions: hold or produce 60. The mistaken producer additionally perceives produce 100, which the scenario does not permit. The severely mismatched producer perceives hold, produce 60, and produce 100 even though the scenario permits only hold.",
        testTreatment: "Varied — the central distinction in this scenario",
      },
      {
        key: "V",
        symbol: "V",
        name: "Valuation",
        definition: "Valuation of actions relative to the agent's objective.",
        mapping:
          "Each action has a fixed value, read from the same declared value map for every producer: hold = 0, produce 60 = 6, produce 100 = 10.",
        testTreatment: "Fixed per action",
      },
      {
        key: "H",
        symbol: "H",
        name: "Time horizon",
        definition: "Which future consequences the agent considers relevant to valuation.",
        mapping: "\"current production decision\"",
        testTreatment: "Fixed",
      },
      {
        key: "D",
        symbol: "D",
        name: "Decision process",
        definition:
          "Process through which the agent selects among perceived feasible actions. It may condition directly on the model of reality and may use valuation when applicable.",
        mapping:
          "Each producer compares its perceived feasible actions and selects the highest-valued one. This comparison only ever considers F̂ — it never checks F_t.",
        testTreatment: "Fixed",
      },
      {
        key: "C",
        symbol: "C",
        name: "Selected action",
        definition: "Action selected by the agent.",
        mapping:
          "The accurate producer selects produce 60. The mistaken and severely mismatched producers both select produce 100 — the highest-valued action in their perceived feasible set.",
        testTreatment: "Endogenously selected",
      },
      {
        key: "O",
        symbol: "O",
        name: "Realized outcome",
        definition: "Realized outcome associated with the selected action.",
        mapping:
          "Realized production, O_{i,t}, once the already-selected action meets the scenario's permission data: 60 units for the accurate producer, 60 units for the mistaken producer (capped down from the 100 it selected), and 0 units for the severely mismatched producer. This is an agent-level specification (Model 5.2); no system outcome O_t is defined. This test's own reality rule never re-runs the decision process or valuation — it only measures how much of the already-selected action the permission data allows. Implementation: capacity_constrained_realization.",
        testTreatment: "Result",
      },
    ],
    assumptions: [
      "This is a framework test of the Model 5.2 outcome step, not a replication of a separate economic theory.",
      "The reality rule used here, capacity_constrained_realization, is specific to this test: it represents a selected action the scenario does not permit by capping realized quantity at the largest quantity among the actions the scenario permits for that producer. This is one admissible way to specify reality's response — other scenarios could specify different consequences, and this test does not claim non-permitted actions universally produce partial realization.",
      "Reality does not call the decision process or valuation again. The selected action remains the action chosen by Model 5.1; failure, partial execution, or changed consequences are represented in the realized outcome. (The current framework also keeps the selected-action record unchanged during outcome realization.)",
      "No learning or feedback occurs in this scenario — it is a single decision period.",
    ],
    hypotheses: [
      "When a producer's perceived feasible set matches the actions the scenario permits, the selected action is fully realized.",
      "When the selected action is perceived feasible but not permitted by the scenario, the realized outcome may be a partial realization of that action, capped by the permission data.",
      "In the current framework, the selected action is recorded as chosen; only the realized outcome differs from what was selected.",
      "Under this test's specific reality rule, a more severe mismatch between F̂ and the permission data can produce a larger shortfall — but this is not asserted as a universal consequence of a selected action not being permitted.",
    ],
    configuration: [
      { label: "Producers", value: "3" },
      { label: "Actions", value: "Hold, produce 60, produce 100" },
      { label: "Values", value: "Hold = 0, produce 60 = 6, produce 100 = 10" },
      {
        label: "Decision process",
        value: "Choose the highest-valued perceived feasible action",
      },
      { label: "Time horizon", value: "Current production decision" },
      {
        label: "Reality rule",
        value: "Realized production is capped at the largest quantity among the actions the scenario permits for that producer",
      },
    ],
    results: [
      {
        label: "Why the mistaken producer only realizes 60",
        value:
          "The mistaken producer selects 100 units because produce 100 is in F̂ and has the highest value. Reality does not change that decision to produce 60. Instead, C remains produce 100 while realized production is limited to 60 units.",
      },
      {
        label: "The severe case",
        value:
          "The severe producer makes the same selection, but with only hold permitted by the scenario, realized production falls to 0.",
      },
    ],
    resultsTable: {
      columns: ["Producer", "Permitted by the scenario", "Perceived feasible F̂", "Selected action C", "Realized O"],
      rows: [
        ["Accurate", "Hold, 60", "Hold, 60", "Produce 60", "60 units"],
        ["Mistaken", "Hold, 60", "Hold, 60, 100", "Produce 100", "60 units"],
        ["Severe mismatch", "Hold", "Hold, 60, 100", "Produce 100", "0 units"],
      ],
    },
    sourcePath: "research/tests/test_feasibility_contract.py",
  },
  {
    slug: "feasible-set-learning",
    runner: "simulation",
    title: "Learning: Feasible Set Discovery",
    category: "Learning",
    summary:
      "An agent at first perceives only one of two permitted actions. Observing its own outcome adds the other to its perceived feasible set, and its next decision selects it.",
    sourceLabel: "Test 22",
    economicQuestion:
      "Can an agent's experience reveal an option it previously overlooked, changing what it chooses the next time?",
    context:
      "An agent makes two decisions between an ordinary action and a better alternative. Initially, it perceives only the ordinary action as available, even though both are objectively permitted. After experiencing its first outcome, the scenario's learning rule adds the better option to its perceived feasible set before the next decision.",
    scope:
      "One agent, two decision points. This illustrates TER Models 5.1, 5.2, and 5.5, not a general process of learning.",
    terComponents: [
      {
        key: "G",
        symbol: "G",
        name: "Objective",
        definition: "Result or condition that provides the reference for valuation when valuation is used.",
        mapping: "Obtain the highest payoff from its choice of action.",
        testTreatment: "Fixed",
      },
      {
        key: "M",
        symbol: "M",
        name: "Model of reality",
        definition:
          "The agent's model of reality, including information, beliefs, assumptions, expectations, and interpretations.",
        mapping:
          "Intentionally empty and fixed in this scenario, so the simulator omits it. M remains part of Model 5.1; this test does not exercise it.",
        testTreatment: "Fixed",
      },
      {
        key: "F",
        symbol: "F_t",
        name: "Objective feasible state of reality",
        definition:
          "The objectively realized conditions and constraints relevant when the selected action(s) at decision point t are realized. Not agent specific, and not an input to the decision process.",
        mapping:
          "Both actions are objectively permitted at both decision points. This is one relevant aspect of F_t, not all of it, and nothing changes it.",
        testTreatment: "Fixed",
      },
      {
        key: "F_hat",
        symbol: "F̂",
        name: "Perceived feasible set",
        definition: "Actions the agent perceives as available to attempt.",
        mapping:
          "Only the ordinary action at the first decision; the update adds the better action before the second.",
        testTreatment: "Updated",
      },
      {
        key: "V",
        symbol: "V",
        name: "Valuation",
        definition: "Valuation of actions relative to the agent's objective.",
        mapping: "Ordinary action 4, better alternative action 9.",
        testTreatment: "Fixed",
      },
      {
        key: "H",
        symbol: "H",
        name: "Time horizon",
        definition: "Which future consequences the agent considers relevant to valuation.",
        mapping: "Ongoing decision.",
        testTreatment: "Fixed",
      },
      {
        key: "D",
        symbol: "D",
        name: "Decision process",
        definition:
          "Process through which the agent selects among perceived feasible actions. It may condition directly on the model of reality and may use valuation when applicable.",
        mapping: "Select the highest-valued action in F̂.",
        testTreatment: "Fixed",
      },
      {
        key: "C",
        symbol: "C",
        name: "Selected action",
        definition: "Action selected by the agent.",
        mapping: "The action D selects at each decision point, returned by the simulator.",
        testTreatment: "Output",
      },
      {
        key: "R",
        symbol: "R",
        name: "Reality function",
        definition:
          "Maps the selected action(s) and the relevant objectively realized state F_t to the realized outcome; its arguments depend on model scope.",
        mapping:
          "Records the selected action as the action the agent experienced. It does not check which actions are permitted or add other consequences.",
        testTreatment: "Fixed",
      },
      {
        key: "O",
        symbol: "O_i,t",
        name: "Realized outcome",
        definition: "Realized outcome associated with the selected action.",
        mapping:
          "The action the agent experienced, returned by the simulator. This is a single-agent specification (Model 5.2), so no system outcome O_t is defined.",
        testTreatment: "Output",
      },
    ],
    assumptions: [
      "Values are scenario-specific assumptions, not TER primitives.",
      "The agent observes its own realized outcome exactly, and nothing else.",
      "The update rule is this scenario's one learning mechanism: after observing that it experienced the ordinary action, the agent adds the better action to F̂. The rule reads only the agent's own state and observation, never F_t.",
      "TER does not claim experience always improves perception, and the test does not model why the agent first missed the better action.",
    ],
    economicSetup:
      "The first decision can select only the ordinary action, because F̂ contains nothing else. The second decision uses the updated F̂ and selects the better action, valued 9 against 4.",
    whatChanges:
      "At first, the agent selects the ordinary action, valued at 4, because it is the only option it perceives. After observing the outcome, its perceived options expand, and it selects the better alternative, valued at 9. The objectively permitted actions never change; only the agent's perception changes through the specified update rule.",
    terNote:
      "Model 5.5 is written from the system outcome O_t; in this single-agent specification, feedback starts from O_{i,t}. Its arrows mark possible influence, not change in every component: here the one update rule changes only F̂.",
    hypotheses: [
      "Premise check: the better action is permitted but not initially perceived.",
      "The first decision is restricted to the ordinary action.",
      "The observed outcome of that decision leads the update to add the better action to F̂ for the next decision.",
      "The next decision selects the better action, now perceived and more highly valued.",
      "The objectively permitted actions do not change during the run; only perception does.",
    ],
    configuration: [
      { label: "Agent", value: "1" },
      { label: "Decision points", value: "2" },
      { label: "Actions and values", value: "Ordinary action = 4, better alternative action = 9" },
      { label: "Initial perceived feasible set", value: "Ordinary action" },
      { label: "Objectively permitted actions", value: "Both actions, at both decision points" },
      { label: "Decision process", value: "Choose the highest-valued perceived feasible action" },
      { label: "Time horizon", value: "Ongoing decision" },
    ],
    implementationMapping: [
      { label: "objective", value: "G" },
      { label: "model_of_reality", value: "M (empty)" },
      { label: "perceived_feasible_set", value: "F̂" },
      { label: "valuation, read by mapped_value", value: "V" },
      { label: "horizon", value: "H" },
      { label: "decision_process = maximize_value", value: "D" },
      { label: "initial_state[\"permitted_actions\"]", value: "Aspect of F_t (permission data)" },
      { label: "trace[t].actions", value: "C_{i,t}" },
      { label: "reality = record_experienced_action", value: "R" },
      { label: "trace[t].reality.agents", value: "O_{i,t}" },
      { label: "observation = observe_own_outcome", value: "What the agent observes of O_{i,t}" },
      { label: "update_rule = learn_from_experience", value: "Model 5.5 update of F̂" },
    ],
    resultsTable: {
      columns: ["Decision point", "F̂ when deciding", "Selected action", "Update after observing O_{i,t}"],
      rows: [
        ["t = 0", "Ordinary", "Ordinary action (4)", "Adds the better action to F̂"],
        ["t = 1", "Ordinary, better", "Better alternative action (9)", "No change"],
      ],
    },
    sourcePath: "research/scenarios/feasible_set_learning.py",
  },
];

export function getScenario(slug: string): Scenario | undefined {
  return scenarios.find((scenario) => scenario.slug === slug);
}
