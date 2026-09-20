/**
 * Presentation metadata for the Learn hub.
 *
 * This file does not define or reinterpret TER. It only describes, for the
 * website, how a given executable replication test maps onto the existing
 * TER architecture. The canonical theory is theory/academic.md; the
 * canonical behavior of each scenario is its executable test under
 * research/tests/. If this file and the test ever disagree, the test wins.
 */

export type ScenarioStatus = "active" | "coming-soon";

/** One row of the core TER decision architecture, as it applies to a scenario. */
export interface TerComponentMapping {
  /** Stable identifier for the variable, independent of display formatting. */
  key: "G" | "M" | "F" | "F_hat" | "V" | "H" | "D" | "C" | "O";
  /** Display form of the symbol, e.g. "F̂" or "F_t" (rendered with a subscript). */
  symbol: string;
  /** Short name of the variable, e.g. "Perceived feasible set". */
  name: string;
  /** General TER definition of the variable (theory/academic.md). */
  definition: string;
  /** How this specific test configures, exercises, or holds this variable. */
  mapping: string;
  /** Short label for how this test treats the variable, e.g. "Fixed across agents". */
  testTreatment: string;
}

export interface ScenarioField {
  label: string;
  value: string;
}

export interface Scenario {
  slug: string;
  status: ScenarioStatus;
  title: string;
  category: string;
  summary: string;
  /** Display identifier for the source this scenario comes from, e.g. "Test 1"
   *  for a numbered replication test or "Model 5.2" for a named theory model.
   *  Rendered as-is; not assumed to be a numbered test. */
  sourceLabel?: string;
  economicQuestion?: string;
  /** Concrete description of how this test's market/agents are set up. */
  economicSetup?: string;
  /** Short statement of what varies across this test's cases vs. what is held fixed. */
  whatChanges?: string;
  terComponents?: TerComponentMapping[];
  assumptions?: string[];
  hypotheses?: string[];
  configuration?: ScenarioField[];
  /** Simple label/value results. Use for tests with a single outcome to report. */
  results?: ScenarioField[];
  /** Comparison table across multiple cases. Use instead of `results` when a test's
   *  point is how the outcome differs across cases (e.g. different decision rules). */
  resultsTable?: { columns: string[]; rows: string[][] };
  /** Path to the executable test, relative to the repository root. */
  sourcePath?: string;
}

export const scenarios: Scenario[] = [
  {
    slug: "basic-agent-choice",
    status: "active",
    title: "Basic Agent Choice",
    category: "Individual choice",
    summary:
      "A single agent chooses its highest-valued action among three coffees it perceives as available.",
    sourceLabel: "Test 1",
    economicQuestion:
      "Can an agent choose its highest-valued perceived feasible action using a specified decision process?",
    economicSetup:
      "A single agent, a coffee buyer, chooses among three coffees — Coffee A, Coffee B, and Coffee C — with hand-assigned values of 4, 7, and 10. The agent perceives all three coffees as available, so its decision process alone determines the selected action.",
    whatChanges:
      "Nothing is varied across cases. This baseline test verifies that when the decision process evaluates every perceived option, the highest-valued action is selected.",
    terComponents: [
      {
        key: "G",
        symbol: "G",
        name: "Objective",
        definition: "Objective pursued by the agent.",
        mapping: "The agent's objective is \"choose coffee.\"",
        testTreatment: "Fixed",
      },
      {
        key: "M",
        symbol: "M",
        name: "Model of reality",
        definition:
          "The agent's model of reality, including information, beliefs, assumptions, expectations, and interpretations.",
        mapping:
          "No distinct information, belief, or expectation is varied in this test.",
        testTreatment: "Fixed",
      },
      {
        key: "F",
        symbol: "F_t",
        name: "Objective feasible state of reality",
        definition:
          "The objective feasible state of reality at time t, including all conditions and constraints that determine what can occur.",
        mapping:
          "F_t and outcome realization are outside this scenario's scope.",
        testTreatment: "Outside scope",
      },
      {
        key: "F_hat",
        symbol: "F̂",
        name: "Perceived feasible set",
        definition: "The possibilities the agent perceives as available.",
        mapping:
          "The agent perceives all three coffees as available.",
        testTreatment: "Fixed",
      },
      {
        key: "V",
        symbol: "V",
        name: "Valuation",
        definition: "Valuation of actions relative to the agent's objective.",
        mapping:
          "Each coffee is assigned a fixed value: Coffee A = 4, Coffee B = 7, Coffee C = 10. These values are held constant for the test. Implementation: ValuationRule.MAPPED.",
        testTreatment: "Fixed per action",
      },
      {
        key: "H",
        symbol: "H",
        name: "Time horizon",
        definition: "Time horizon considered relevant to the decision.",
        mapping: "\"current decision\"",
        testTreatment: "Fixed",
      },
      {
        key: "D",
        symbol: "D",
        name: "Decision process",
        definition:
          "Decision process used to evaluate and select among perceived feasible actions.",
        mapping:
          "The agent compares all perceived feasible coffees and selects the one with the highest assigned value. Implementation: DecisionProcess.MAXIMIZE.",
        testTreatment: "Fixed",
      },
      {
        key: "C",
        symbol: "C",
        name: "Selected action",
        definition: "Action selected by the agent.",
        mapping: "The agent selects the highest-valued coffee: Coffee C.",
        testTreatment: "Endogenously selected",
      },
      {
        key: "O",
        symbol: "O",
        name: "Realized outcome",
        definition: "Realized outcome associated with the selected action.",
        mapping:
          "Outside this scenario's scope. This scenario ends with the selected action.",
        testTreatment: "Not tested",
      },
    ],
    assumptions: [
      "Values are a static, hand-assigned map, not derived from any utility function.",
    ],
    hypotheses: [
      "The agent selects the highest-valued action in its perceived feasible set.",
    ],
    configuration: [
      { label: "Actions", value: "Coffee A, Coffee B, Coffee C" },
      { label: "Values", value: "Coffee A = 4, Coffee B = 7, Coffee C = 10" },
      { label: "Perceived feasible set", value: "Coffee A, Coffee B, Coffee C" },
      {
        label: "Valuation method",
        value: "Fixed values assigned to each coffee (ValuationRule.MAPPED)",
      },
      {
        label: "Decision process",
        value:
          "Compare all perceived feasible options and choose the highest-valued one (DecisionProcess.MAXIMIZE)",
      },
      { label: "Time horizon", value: "Current decision" },
    ],
    results: [{ label: "Selected action", value: "Coffee C (10)" }],
    sourcePath: "research/tests/test_01_basic_agent_choice.py",
  },
  {
    slug: "bounded-rationality",
    status: "active",
    title: "Bounded Rationality",
    category: "Individual choice",
    summary:
      "The same coffee buyer picks a different coffee once its decision process only searches part of its perceived feasible set — TER does not require universal optimization.",
    sourceLabel: "Test 3",
    economicQuestion:
      "Can TER represent a nonoptimal choice produced by limited search rather than universal optimization?",
    economicSetup:
      "The same single agent, a coffee buyer, chooses among three coffees — Nearby Coffee, Office Coffee, and Best Coffee — with hand-assigned values of 6, 7, and 10. The agent perceives all three coffees as available in every case. Only the agent's decision process, how many of those perceived feasible actions it searches, and the order it searches them in are varied.",
    whatChanges:
      "The objective, perceived feasible set, valuations, and time horizon stay fixed. Only the decision process's configuration changes — the decision process, search depth, and search order — to see whether the selected action changes.",
    terComponents: [
      {
        key: "G",
        symbol: "G",
        name: "Objective",
        definition: "Objective pursued by the agent.",
        mapping: "The agent's objective is \"choose preferred coffee.\"",
        testTreatment: "Fixed",
      },
      {
        key: "M",
        symbol: "M",
        name: "Model of reality",
        definition:
          "The agent's model of reality, including information, beliefs, assumptions, expectations, and interpretations.",
        mapping:
          "No distinct information, belief, or expectation is varied in this test.",
        testTreatment: "Fixed",
      },
      {
        key: "F",
        symbol: "F_t",
        name: "Objective feasible state of reality",
        definition:
          "The objective feasible state of reality at time t, including all conditions and constraints that determine what can occur.",
        mapping:
          "F_t and outcome realization are outside this scenario's scope.",
        testTreatment: "Outside scope",
      },
      {
        key: "F_hat",
        symbol: "F̂",
        name: "Perceived feasible set",
        definition: "The possibilities the agent perceives as available.",
        mapping:
          "The same three coffees, in the same order, in every case. Only the decision process's search configuration changes across cases — not which coffees the agent perceives as feasible.",
        testTreatment: "Fixed",
      },
      {
        key: "V",
        symbol: "V",
        name: "Valuation",
        definition: "Valuation of actions relative to the agent's objective.",
        mapping:
          "Each coffee has a fixed value, read directly from the same declared value map used in Test 01: Nearby Coffee = 6, Office Coffee = 7, Best Coffee = 10. Implementation: ValuationRule.MAPPED.",
        testTreatment: "Fixed per action",
      },
      {
        key: "H",
        symbol: "H",
        name: "Time horizon",
        definition: "Time horizon considered relevant to the decision.",
        mapping: "\"current purchase\"",
        testTreatment: "Fixed",
      },
      {
        key: "D",
        symbol: "D",
        name: "Decision process",
        definition:
          "Decision process used to evaluate and select among perceived feasible actions.",
        mapping:
          "The agent either checks every perceived feasible coffee before deciding (exhaustive search), or stops after checking only the first few, in its search order (limited search). Implementation: DecisionProcess.MAXIMIZE for exhaustive search; DecisionProcess.LIMITED_SEARCH for limited search.",
        testTreatment: "Varied across cases",
      },
      {
        key: "C",
        symbol: "C",
        name: "Selected action",
        definition: "Action selected by the agent.",
        mapping:
          "Best Coffee under exhaustive search; Office Coffee under limited search (depth 2); Best Coffee under broader search (depth 3); Best Coffee under limited search once the order is changed.",
        testTreatment: "Endogenously selected; differs by decision process, search depth, and search order",
      },
      {
        key: "O",
        symbol: "O",
        name: "Realized outcome",
        definition: "Realized outcome associated with the selected action.",
        mapping:
          "Outside this scenario's scope. This scenario ends with the selected action.",
        testTreatment: "Not tested",
      },
    ],
    assumptions: [
      "search_limit is a test-specific decision-rule parameter, not a TER primitive; it controls how many perceived feasible actions DecisionProcess.LIMITED_SEARCH considers.",
      "Search order is a decision-process parameter (search_order), not a reordering of the perceived feasible set, which is identical, in the same order, in every case.",
    ],
    hypotheses: [
      "Exhaustive search selects the highest-valued action.",
      "Limited search can select a lower-valued action.",
      "Increasing search depth can change the selected action.",
      "Search order can matter under incomplete search.",
    ],
    configuration: [
      { label: "Actions", value: "Nearby Coffee, Office Coffee, Best Coffee" },
      { label: "Values", value: "Nearby Coffee = 6, Office Coffee = 7, Best Coffee = 10" },
      {
        label: "Perceived feasible set",
        value: "Nearby Coffee, Office Coffee, Best Coffee (identical, in the same order, in every case)",
      },
      {
        label: "Valuation method",
        value: "Fixed values assigned to each coffee (ValuationRule.MAPPED)",
      },
      { label: "Time horizon", value: "Current purchase" },
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
    sourcePath: "research/tests/test_03_bounded_rationality.py",
  },
  {
    slug: "supply-and-demand",
    status: "active",
    title: "Supply and Demand",
    category: "Markets",
    summary:
      "Independent buyer and seller decisions aggregate into demand, supply, and a market-clearing price.",
    sourceLabel: "Test 7",
    economicQuestion:
      "Can independent buyer and seller decisions aggregate into downward-sloping demand, upward-sloping supply, and predictable changes in market-clearing price?",
    economicSetup:
      "The market contains five buyers with reservation values of 9, 8, 7, 6, and 5, and five sellers with costs of 1, 2, 3, 4, and 5. At each candidate price from 1 through 9, buyers independently choose whether to buy and sellers independently choose whether to sell. Their decisions determine quantity demanded, quantity supplied, excess demand, and whether that price clears the market.",
    whatChanges:
      "Each buyer and seller keeps the same specification across a range of candidate prices; only the quoted price changes. The test counts their individual buy and sell decisions at each candidate price to find where the market clears. The test then changes demand or supply by adding one agent and checks whether the clearing price moves in the expected direction.",
    terComponents: [
      {
        key: "G",
        symbol: "G",
        name: "Objective",
        definition: "Objective pursued by the agent.",
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
          "The objective feasible state of reality at time t, including all conditions and constraints that determine what can occur.",
        mapping: "F_t and outcome realization are outside this scenario's scope.",
        testTreatment: "Outside scope",
      },
      {
        key: "F_hat",
        symbol: "F̂",
        name: "Perceived feasible set",
        definition: "The possibilities the agent perceives as available.",
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
          "Buyers value buying according to the difference between their reservation value and the quoted price. Sellers value selling according to the difference between the quoted price and their cost. Because reservation values and costs differ across agents, the same price can lead different agents to make different choices. Implementation: ValuationRule.PRICE_TAKING.",
        testTreatment: "Varies across agents and prices",
      },
      {
        key: "H",
        symbol: "H",
        name: "Time horizon",
        definition: "Time horizon considered relevant to the decision.",
        mapping: "\"current transaction\"",
        testTreatment: "Fixed",
      },
      {
        key: "D",
        symbol: "D",
        name: "Decision process",
        definition: "Decision process used to evaluate and select among perceived feasible actions.",
        mapping:
          "Each buyer compares buying with not buying, and each seller compares selling with not selling. The action with the higher value is selected. If the two actions have equal value, the test is configured so the agent transacts. Implementation: DecisionProcess.MAXIMIZE.",
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
    status: "active",
    title: "Asymmetric Information",
    category: "Information",
    summary:
      "High-quality sellers withdraw when individual quality cannot be observed and the market prices goods using pooled expected quality.",
    sourceLabel: "Test 4",
    economicQuestion:
      "Can TER represent the adverse-selection mechanism in Akerlof's \"market for lemons,\" where high-quality sellers withdraw when individual quality is unobservable and goods are priced using pooled expected quality?",
    economicSetup:
      "The market contains three high-quality sellers and three low-quality sellers. High-quality goods are worth 10, and their sellers have a reservation value of 8. Low-quality goods are worth 4, and their sellers have a reservation value of 2. The market initially believes that 50% of the goods for sale are high quality. Every seller chooses between selling at the offered price and holding onto the good.",
    whatChanges:
      "The sellers, reservation values, perceived feasible sets, and decision process stay the same. The test changes what quality information the pricing mechanism can use. Under pooled pricing, individual quality is unobservable. Under verified pricing, each seller's quality can be used directly.",
    terComponents: [
      {
        key: "G",
        symbol: "G",
        name: "Objective",
        definition: "Objective pursued by the agent.",
        mapping: "Every seller seeks to maximize proceeds from selling.",
        testTreatment: "Fixed",
      },
      {
        key: "M",
        symbol: "M",
        name: "Model of reality",
        definition:
          "The agent's model of reality, including information, beliefs, assumptions, expectations, and interpretations.",
        mapping:
          "Each seller's model includes its own car's quality, which the reality rule never reads. What changes between the two cases is the quality information available to the pricing mechanism: pooled pricing cannot use individual quality, while verified pricing can.",
        testTreatment: "Each seller's own model is fixed; the pricing mechanism's access to it varies",
      },
      {
        key: "F",
        symbol: "F_t",
        name: "Objective feasible state of reality",
        definition:
          "The objective feasible state of reality at time t, including all conditions and constraints that determine what can occur.",
        mapping:
          "The reality rule reads each car's actual quality, a scenario-specified condition that represents one relevant aspect of F_t. It is not a complete representation of F_t.",
        testTreatment: "Fixed",
      },
      {
        key: "F_hat",
        symbol: "F̂",
        name: "Perceived feasible set",
        definition: "The possibilities the agent perceives as available.",
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
          "A seller evaluates selling as the offered price minus its reservation value, which represents the opportunity cost of giving up the good. Implementation: ValuationRule.NET.",
        testTreatment: "Varies with the price offered and each seller's reservation value",
      },
      {
        key: "H",
        symbol: "H",
        name: "Time horizon",
        definition: "Time horizon considered relevant to the decision.",
        mapping: "\"current sale decision\"",
        testTreatment: "Fixed",
      },
      {
        key: "D",
        symbol: "D",
        name: "Decision process",
        definition:
          "Decision process used to evaluate and select among perceived feasible actions.",
        mapping:
          "Each seller compares selling with holding and selects the higher-valued option. Implementation: DecisionProcess.MAXIMIZE.",
        testTreatment: "Fixed",
      },
      {
        key: "C",
        symbol: "C",
        name: "Selected action",
        definition: "Action selected by the agent.",
        mapping: "Each seller selects either sell or hold.",
        testTreatment: "Endogenously selected",
      },
      {
        key: "O",
        symbol: "O",
        name: "Realized outcome",
        definition: "Realized outcome associated with the selected action.",
        mapping:
          "The reality rule takes all sellers' selected actions together, with each car's actual quality, and produces the system outcome O_t: how many high-quality and low-quality goods are sold, and the total. This is a multi-agent specification; no individual outcomes O_{i,t} are defined. Implementation: RealityFunction.QUALITY_MARKET.",
        testTreatment: "Result",
      },
    ],
    assumptions: [
      "Buyers are not represented as individual TER agents in this test. The market price each seller faces is set directly as a fixed valuation input, not computed by a separate buyer agent or rule.",
      "Under pooled pricing, every seller's valuation is initialized with the same population-level price (based on the believed share of high-quality goods) — the same price regardless of the seller's own quality.",
      "Under verified pricing, each seller's valuation is instead initialized with its own true price, so a seller's quality determines the price it faces.",
      "Both prices are fixed scenario data, set directly in each seller's initial valuation (V) via ValuationRule.NET — not TER feedback, since neither price depends on a realized outcome.",
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
    sourcePath: "research/tests/test_04_asymmetric_information.py",
  },
  {
    slug: "externalities",
    status: "active",
    title: "Externalities",
    category: "Externalities",
    summary:
      "A privately profitable action can create a negative external effect and produce lower total value under a specified social-value measure.",
    sourceLabel: "Test 8",
    economicQuestion:
      "Can a privately preferred action create a negative external effect and produce a lower value under a specified social-value measure, and can internalizing that effect in the firm's own valuation change the action it selects?",
    economicSetup:
      "One firm chooses between producing and not producing. Producing gives the firm a private value of 4, but also creates an external effect on others represented by −7. Not producing has a private value of 0 and an external effect of 0. The firm perceives both actions as available, and its objective and decision process are the same in both cases considered below.",
    whatChanges:
      "Everything except the firm's valuation treatment stays the same. In the private-incentive case, the firm considers only its own private value. In the internalized case, the firm's valuation also includes the external effect.",
    terComponents: [
      {
        key: "G",
        symbol: "G",
        name: "Objective",
        definition: "Objective pursued by the agent.",
        mapping: "The firm seeks to maximize firm net value.",
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
          "The objective feasible state of reality at time t, including all conditions and constraints that determine what can occur.",
        mapping:
          "The reality rule reads the scenario's actual private values and external effects for each action, and the actions permitted for the firm. These are scenario-specified conditions that represent relevant aspects of F_t, not a complete representation of it.",
        testTreatment: "Fixed",
      },
      {
        key: "F_hat",
        symbol: "F̂",
        name: "Perceived feasible set",
        definition: "The possibilities the agent perceives as available.",
        mapping: "The firm perceives both actions as available.",
        testTreatment: "Fixed",
      },
      {
        key: "V",
        symbol: "V",
        name: "Valuation",
        definition: "Valuation of actions relative to the agent's objective.",
        mapping:
          "The only TER input that changes between the two cases. Private-incentive valuation counts only the firm's own gain; internalized valuation adds the external effect on top of that same gain. Both read the same underlying private-value and external-effect facts — only how they're combined differs. Implementation: ValuationRule.PRIVATE for the private-incentive case, ValuationRule.INTERNALIZED for the internalized case.",
        testTreatment: "Varied across cases",
      },
      {
        key: "H",
        symbol: "H",
        name: "Time horizon",
        definition: "Time horizon considered relevant to the decision.",
        mapping: "\"current production decision\"",
        testTreatment: "Fixed",
      },
      {
        key: "D",
        symbol: "D",
        name: "Decision process",
        definition:
          "Decision process used to evaluate and select among perceived feasible actions.",
        mapping:
          "The firm compares all perceived feasible actions and selects the one with the highest value. Implementation: DecisionProcess.MAXIMIZE.",
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
          "The reality rule takes the selected action and the scenario's own private-value and external-effect data and reports O_{i,t}: the private value, the external effect, and this test's specified social value, defined here as private value plus external effect. This is a single-agent specification, so no system outcome O_t is defined. Implementation: RealityFunction.SOCIAL_VALUE.",
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
    status: "active",
    title: "Perceived Feasibility vs. Scenario Permission",
    category: "Feasibility",
    summary:
      "A producer may select an action the scenario does not permit. The selected action stays the one the decision process chose; the realized outcome shows what the scenario allowed.",
    sourceLabel: "Model 5.2",
    economicQuestion:
      "When an agent's perceived feasible set includes an action the scenario does not permit, does the selected action remain the action the agent chose while the realized outcome is limited by the scenario's permission data rather than re-decided?",
    economicSetup:
      "Three producers choose a production action: hold (0 units), produce 60, or produce 100. Producing 60 is valued at 6 and producing 100 is valued at 10; holding is valued at 0. The three producers share the same objective, values, time horizon, and decision process. They differ only in which actions the scenario permits for them and which actions they perceive as feasible.",
    whatChanges:
      "The producers use the same objective, valuation, horizon, and decision process. What differs is the relationship between what each producer perceives as feasible and what the scenario permits: the accurate producer perceives exactly the permitted actions, the mistaken producer perceives one extra action that isn't permitted, and the severely mismatched producer perceives two production actions that aren't permitted. This is a single-period test — it does not involve learning or feedback between periods.",
    terComponents: [
      {
        key: "G",
        symbol: "G",
        name: "Objective",
        definition: "Objective pursued by the agent.",
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
          "The objective feasible state of reality at time t, including all conditions and constraints that determine what can occur.",
        mapping:
          "The scenario's permission data lists the permitted actions for each producer: hold or produce 60 for the accurate and mistaken producers, hold only for the severely mismatched producer. This data represents the relevant constraint (a production ceiling) in this implementation; it is not F_t itself.",
        testTreatment: "Varied across producers",
      },
      {
        key: "F_hat",
        symbol: "F̂",
        name: "Perceived feasible set",
        definition: "The possibilities the agent perceives as available.",
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
          "Each action has a fixed value, read from the same declared value map for every producer: hold = 0, produce 60 = 6, produce 100 = 10. Implementation: ValuationRule.MAPPED.",
        testTreatment: "Fixed per action",
      },
      {
        key: "H",
        symbol: "H",
        name: "Time horizon",
        definition: "Time horizon considered relevant to the decision.",
        mapping: "\"current production decision\"",
        testTreatment: "Fixed",
      },
      {
        key: "D",
        symbol: "D",
        name: "Decision process",
        definition:
          "Decision process used to evaluate and select among perceived feasible actions.",
        mapping:
          "Each producer compares its perceived feasible actions and selects the highest-valued one. This comparison only ever considers F̂ — it never checks F_t. Implementation: DecisionProcess.MAXIMIZE.",
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
];

export function getScenario(slug: string): Scenario | undefined {
  return scenarios.find((scenario) => scenario.slug === slug);
}

export function getActiveScenarios(): Scenario[] {
  return scenarios.filter((scenario) => scenario.status === "active");
}
