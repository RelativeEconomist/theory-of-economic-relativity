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

import { lotteryTerComponents } from "./lottery-tickets";

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

export interface ResultsTable {
  columns: string[];
  rows: string[][];
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
  /** Opening paragraphs, shown without a heading. */
  introduction: string[];
  /** Heading of the lesson's activity, e.g. "Try it" or "Worked example". */
  activityHeading: string;
  /** What to do in the activity, shown below its heading. */
  instruction?: string;
  /** A fixed demonstration's result, shown as the activity. */
  workedExample?: { table: ResultsTable; note?: string };
  /** Paragraphs for the lesson's "What this shows" section. Text in this
   *  field, `configuration`, and `formalModel` may mark TER symbols in
   *  braces, e.g. "{V}", to render them as notation. */
  takeaway: string[];
  /** A phrase in the takeaway rendered as a link, e.g. to a related lesson. */
  takeawayLink?: { text: string; href: string };
  /** Short orientation before the activity: the TER components the reader
   *  works with, and what changes in the experiment. Not the full model. */
  configuration?: { table: ResultsTable; note: string };
  /** Visible formal model after the takeaway: an opening sentence (the
   *  models it names link to the theory), the equations, these paragraphs,
   *  the full TER mapping, and a closing sentence. */
  formalModel: {
    /** Section heading; "Formal model" when omitted. */
    heading?: string;
    /** False for a lesson that describes a choice without TER's equations. */
    equations?: boolean;
    introduction: string;
    /** Also show the single-agent Model 5.2 outcome equation. */
    outcomeModel?: boolean;
    explanation: string[];
    closing: string;
  };
  /** One-sentence scope statement, opening Model details. */
  scope?: string;
  /** Paragraphs in Model details, before the TER model. */
  modelDetails?: string[];
  /** TER-terms note, shown after the TER model in Model details. */
  terNote?: string;
  terComponents?: TerComponentMapping[];
  assumptions?: string[];
  /** Results of the default configuration, shown in Model details so they are
   *  not mistaken for the current run. `checks` lists that configuration's
   *  hypotheses. */
  referenceResults?: {
    heading: string;
    /** Sentence before the reference results, e.g. the configuration they use. */
    intro?: string;
    table?: ResultsTable;
    results?: ScenarioField[];
    checks?: string[];
  };
  hypotheses?: string[];
  /** Opening sentence of Implementation and verification. */
  implementationNote?: string;
  /** Python fields (label) and the TER variable each one specifies (value). */
  implementationMapping?: ScenarioField[];
  /** Path to the executable test or scenario, relative to the repository root. */
  sourcePath?: string;
  /** Path to a separate replication test, relative to the repository root. */
  testPath?: string;
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
    introduction: [
      "Three coffees are available. In this example, each has an assigned score representing how the agent values it. Higher scores mean higher value; they are not prices.",
      "The agent uses a simple rule: choose the coffee with the highest score.",
    ],
    activityHeading: "Try it",
    instruction:
      "Leave Coffee A at 4 and Coffee C at 10. Before running, predict which coffee will be selected when Coffee B’s score is 9, then 11. Run each case to check your prediction.",
    configuration: {
      table: {
        columns: ["Component", "Role in this example"],
        rows: [
          ["Perceived feasible set, {F̂}", "Coffee A, B, and C are the options considered available."],
          ["Valuation, {V}", "You assign a score to each coffee."],
          ["Decision process, {D}", "Select the coffee with the highest score."],
          ["Selected action, {C}", "The coffee selected by that process."],
        ],
      },
      note: "In this experiment, you change the valuations while the options and decision process stay fixed.",
    },
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
    takeaway: [
      "The scores are the valuations, {V}. The decision process, {D}, compares those scores and selects an action, {C}, from the perceived feasible set, {F̂}.",
      "Changing {V} can change {C} even when {D} and {F̂} stay fixed. A score can also change without changing the choice if the same coffee remains highest.",
    ],
    formalModel: {
      introduction: "This example uses TER Model 5.1, the Agent Decision Model.",
      explanation: [
        "For agent {i} at decision point {t}, {D} selects {C} from the perceived feasible set {F̂}. Model 5.1 allows the decision process to use the agent’s model of reality, {M}, and valuation, {V}. Where valuation is used, it is conditioned on the objective, {G}, model of reality, {M}, and time horizon, {H}.",
        "In this configuration, {V} reads the scores assigned to the coffees, and {D} selects the highest score. {M} is empty and is not used by either rule. {G} and {H} are specified, but the assigned scores do not vary with them.",
      ],
      closing: "The simulation ends with the selected action. It does not model buying or consuming the coffee.",
    },
    modelDetails: [
      "Scores are assigned directly, without modeling how they were formed.",
      "When the highest scores are equal, the rule selects the first tied option in this order: Coffee A, Coffee C, Coffee B.",
      "TER can represent other decision rules. Choosing the highest value is the rule used in this example.",
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
    testPath: "research/tests/test_01_basic_agent_choice.py",
  },
  {
    slug: "bounded-rationality",
    runner: "simulator",
    title: "Bounded Rationality",
    category: "Individual choice",
    summary:
      "The same coffee buyer picks a different coffee once its decision process only searches part of its perceived feasible set — TER does not require universal optimization.",
    sourceLabel: "Test 3",
    introduction: [
      "Three coffees are available. Each has a score representing how the agent values it. Higher scores mean higher value; they are not prices.",
      "The agent can check every coffee or limit its search to the first few in a specified order. It chooses the highest score among the coffees it checks. Can the choice change without changing the scores?",
    ],
    activityHeading: "Try it",
    instruction:
      "Start with the default scores and search order. Limited search checks Nearby Coffee and Office Coffee first. Predict what happens when you increase the number of coffees checked from 2 to 3, then run to check your prediction.",
    configuration: {
      table: {
        columns: ["Component", "Role in this example"],
        rows: [
          ["Perceived feasible set, {F̂}", "All three coffees remain available under both decision processes."],
          ["Valuation, {V}", "Each coffee has an assigned score."],
          [
            "Decision process, {D}",
            "Check every coffee, or only the first few in the search order. Select the highest score among those checked.",
          ],
          ["Selected action, {C}", "The coffee selected by that process."],
        ],
      },
      note: "In the experiment below, keep the scores fixed and change the search limit within {D}. This changes which coffees are checked without changing {F̂}.",
    },
    takeaway: [
      "A coffee can belong to the perceived feasible set, {F̂}, without being checked by the decision process, {D}. Limited search can therefore miss an option with a higher valuation, {V}.",
      "Basic Agent Choice changes valuations while keeping the decision process fixed. This experiment changes the search performed by {D} while keeping the scores fixed. Either change can affect the selected action, {C}.",
    ],
    takeawayLink: { text: "Basic Agent Choice", href: "/learn/basic-agent-choice/" },
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
          "Check all coffees evaluates every option; limited search evaluates only the first few in its search order. Both select the highest score among the coffees checked.",
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
    formalModel: {
      introduction: "This example uses TER Model 5.1, the Agent Decision Model.",
      explanation: [
        "{D} selects an action {C} from the perceived feasible set {F̂}. In this configuration, {V} supplies the coffee scores. The two decision processes differ in which scores they inspect before selecting an action.",
        "Checking all coffees evaluates every option in {F̂}. Limited search evaluates only the first options in its configured search order, up to the search limit. Both select the highest score among the options they check.",
        "The search limit and search order configure {D}; they do not remove options from {F̂}. {M} is empty and is not used by either rule. {G} and {H} are specified, but the assigned scores do not vary with them.",
      ],
      closing: "The simulation ends with the selected action. It does not model buying or consuming the coffee.",
    },
    modelDetails: [
      "This example represents one agent making one decision. Scores are assigned directly, without modeling how they were formed.",
      "When checking all coffees, ties go to the first tied option in this order: Nearby Coffee, Office Coffee, Best Coffee. Under limited search, ties go to the first tied coffee in the configured search order.",
      "Limited search is one possible specification of bounded rationality. This example does not model search costs, time pressure, or how the search limit is determined.",
      "TER can represent other decision processes. Neither checking every option nor choosing the highest score is required in every TER configuration.",
    ],
    hypotheses: [
      "Checking all coffees selects a coffee with the highest score.",
      "Limited search can select a coffee with a lower score than an unchecked option.",
      "Increasing the search limit can change the selected action.",
      "Changing the search order can change which options a limited search checks.",
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
    referenceResults: {
      heading: "Default score examples",
      table: {
        columns: ["Case", "Coffees checked", "Selected action"],
        rows: [
          ["Check all coffees", "All three", "Best Coffee (10)"],
          ["Limited search", "Nearby Coffee, Office Coffee", "Office Coffee (7)"],
          ["Search limit increased to 3", "All three", "Best Coffee (10)"],
        ],
      },
    },
    sourcePath: "research/scenarios/bounded_rationality.py",
    testPath: "research/tests/test_03_bounded_rationality.py",
  },
  {
    slug: "pokemon-card-choice",
    title: "Pokémon: Trade or sell?",
    sourceLabel: "Trade or sell?",
    category: "Individual choice",
    summary: "Would you complete your collection or try to sell for more?",
    introduction: [
      "You have a spare Pokémon card with an estimated market price of $100. A friend offers you a card with an estimated market price of $90. It is the last card you need to complete your collection.",
      "You could make the trade now, or try to sell your spare card for $115. Finding a buyer at that price is not guaranteed.",
    ],
    activityHeading: "Would you complete your collection or try to sell for more?",
    configuration: {
      table: {
        columns: ["Component", "Role in this exercise"],
        rows: [
          ["Objective, {G}", "What you want from the decision, such as completing the collection or obtaining money."],
          [
            "Model of reality, {M}",
            "The stated prices, collection details, and uncertainty about finding a buyer.",
          ],
          [
            "Valuation, {V}",
            "How you weigh the trade against attempting a sale. The exercise does not assign scores.",
          ],
          ["Selected action, {C}", "The option you choose."],
        ],
      },
      note: "The exercise records your selections on this page. It does not calculate your valuations or specify your decision process.",
    },
    takeaway: [
      "Same prices. Different circumstances. A choice that could change or stay the same.",
      "TER helps us distinguish the circumstances described in {M}, the objectives represented by {G}, the valuations represented by {V}, and the selected action {C}. Your answers show your choices; they do not identify a complete configuration of those components.",
    ],
    // A reader choice exercise: TER describes the choice without an equation.
    formalModel: {
      heading: "TER interpretation",
      equations: false,
      introduction:
        "This exercise uses TER to describe a choice, not to calculate it. The second situation changes the stated collection circumstances while keeping the prices the same.",
      explanation: [],
      closing:
        "A changed choice does not identify a unique cause, and an unchanged choice does not show that nothing about your evaluation changed.",
    },
    terComponents: [
      {
        key: "G",
        symbol: "G",
        name: "Objective",
        definition:
          "Result or condition that provides the reference for valuation when valuation is used.",
        mapping:
          "Completing a collection and obtaining money are possible objectives. Your selections do not establish which objectives you held.",
      },
      {
        key: "M",
        symbol: "M",
        name: "Model of reality",
        definition:
          "The agent's model of reality, including information, beliefs, assumptions, expectations, and interpretations.",
        mapping:
          "The situations provide different information about whether the offered card completes your collection. They also describe estimated prices and an uncertain opportunity to sell.",
      },
      {
        key: "V",
        symbol: "V",
        name: "Valuation",
        definition:
          "Valuation of actions relative to the agent's objective.",
        mapping:
          "The trade can matter for reasons beyond its estimated market price. Your answers do not reveal numerical valuations for either option.",
      },
      {
        key: "D",
        symbol: "D",
        name: "Decision process",
        definition:
          "Process through which the agent selects among perceived feasible actions. It may condition directly on the model of reality and may use valuation when applicable.",
        mapping:
          "The exercise does not specify how you reached your choices.",
      },
      {
        key: "C",
        symbol: "C",
        name: "Selected action",
        definition:
          "Action selected by the agent.",
        mapping:
          "Your selected option in each situation.",
      },
      {
        key: "O",
        symbol: "O",
        name: "Realized outcome",
        definition:
          "Realized outcome associated with the selected action.",
        mapping:
          "No transaction is carried out. A selection does not establish that a trade or sale occurred.",
      },
    ],
    modelDetails: [
      "This is a hypothetical choice exercise with two stated options. Prices are illustrative, and selling fees are excluded.",
      "The friend is ready to trade. Receiving money from a sale depends on finding a buyer who completes it.",
      "The exercise does not model bargaining, buying another card after a sale, or the friend’s decision process.",
      "Responses can motivate investigation, but they do not establish why people behave as they do.",
    ],
    implementationNote:
      "Choices are held in page memory and cleared when the page is reloaded. This exercise does not call the TER simulation API.",
  },
  {
    slug: "lottery-tickets",
    runner: "simulator",
    title: "Lottery Tickets",
    sourceLabel: "Test 28",
    category: "Individual choice",
    summary: "Three explanations predict the same ticket purchase. Which conditions tell them apart?",
    introduction: [
      "Would you spend $20 for a one in a million chance to win $10 million?",
      "Alex has $50 available. A ticket costs $20. If it wins, he receives $10 million. Otherwise, he loses the ticket price.",
      "Alex might overestimate his chances, enjoy playing, or buy out of habit. The same purchase can have different explanations.",
    ],
    activityHeading: "Try it",
    instruction:
      "Start with the default ticket price and jackpot. Tell Alex the actual chance of winning, then run the simulation. Switch between the three explanations to see whether the same information changes his choice.",
    configuration: {
      table: {
        columns: ["Component", "Role in this example"],
        rows: [
          [
            "Objective, {G}",
            "The valuation-based explanations pursue money, or money plus enjoyment. The routine does not consult {G}.",
          ],
          [
            "Model of reality, {M}",
            "Alex’s information about the ticket and, where used, his believed chance of winning.",
          ],
          ["Valuation, {V}", "The valuation-based explanations compare buying with skipping. The routine does not use {V}."],
          ["Decision process, {D}", "Compare valuations, or follow the specified purchase routine."],
          ["Selected action, {C}", "Buy or skip the ticket."],
          [
            "Realized outcome, {O}",
            "Possible monetary outcomes and their probabilities under the actual lottery conditions.",
          ],
        ],
      },
      note: "Choose an explanation to specify how Alex decides. Changing the ticket conditions lets you compare what the three configurations predict.",
    },
    takeaway: [
      "The same purchase can follow from different configurations of {G}, {M}, {V}, and {D}. A choice alone does not identify which explanation produced it.",
      "Changing the conditions lets us compare those explanations. Revealing the actual odds changes the mistaken belief when that configuration accepts the information, but the resulting choice still depends on the price and jackpot.",
      "These are specified explanations to investigate, not conclusions about a real person’s motives.",
    ],
    formalModel: {
      introduction: "This example uses TER Model 5.1 for Alex’s choice and Model 5.2 for the outcome representation.",
      outcomeModel: true,
      explanation: [
        "In the first two configurations, {V} compares buying with skipping, and {D} selects the higher valuation. The mistaken odds configuration uses Alex’s believed probability. The enjoyment configuration also includes an assigned enjoyment value of $15.",
        "The routine uses a different {D}: buy when the ticket is affordable and costs $30 or less. It does not consult {G}, {V}, or {H}.",
        "{R} maps the selected action and a particular draw state to a monetary outcome. The simulator applies {R} to the possible draw states and weights the outcomes by their actual probabilities. It reports this distribution rather than drawing a ticket.",
      ],
      closing: "Enjoyment affects valuation in its configuration. It is not money received and is excluded from the monetary outcome calculation.",
    },
    scope:
      "One fictional buyer and one decision. These explanations illustrate possible mechanisms; they do not establish why real lottery players buy tickets.",
    // The lesson's short assumptions merged with its detailed ones, each idea once.
    assumptions: [
      "Alex has $50 and can buy at most one ticket.",
      "Alex knows the ticket price, jackpot, and available funds correctly.",
      "Disclosed odds are accepted as credible. Actual odds remain unchanged.",
      "The lottery has one prize and no other payouts. Taxes, shared prizes, and annuity options are omitted.",
      "Enjoyment is valued at $15 regardless of price, jackpot, or odds. Realized enjoyment is not modeled.",
      "Each configuration represents one decision about one draw. Repeated purchases and learning from outcomes are not modeled.",
      "Each configuration’s rules and parameters stay fixed as conditions change.",
      "Different configurations may remain indistinguishable under some conditions.",
    ],
    hypotheses: [
      "The configurations produce the same initial choice but different choices under some changes in conditions.",
    ],
    // The default configuration; the simulator's selector swaps the mapping text.
    terComponents: lotteryTerComponents("alex_mistaken_odds"),
    sourcePath: "research/scenarios/lottery_tickets.py",
    testPath: "research/tests/test_28_lottery_tickets.py",
  },
  {
    slug: "supply-and-demand",
    title: "Supply and Demand",
    category: "Markets",
    summary:
      "Independent buyer and seller decisions aggregate into demand, supply, and a market-clearing price.",
    sourceLabel: "Test 7",
    introduction: [
      "At a given price, how many buyers want to buy, and how many sellers want to sell?",
      "This example has five buyers willing to pay up to 9, 8, 7, 6, and 5, and five sellers with costs of 1, 2, 3, 4, and 5. The model compares their choices at prices from 1 to 9.",
      "A buyer participates when the price is no higher than their limit. A seller participates when the price covers their cost, including when the two are equal.",
    ],
    activityHeading: "Worked example",
    instruction: "Compare the original market with two changes: adding one buyer, or adding one seller.",
    workedExample: {
      table: {
        columns: ["Market", "Change from the original market", "Clearing price"],
        rows: [
          ["Original market", "None", "5"],
          ["Additional buyer", "One buyer willing to pay up to 10", "6"],
          ["Additional seller", "One seller with a cost of 4", "4"],
        ],
      },
      note: "A clearing price is one where the number of buyers choosing to buy equals the number of sellers choosing to sell.",
    },
    configuration: {
      table: {
        columns: ["Component", "Role in this example"],
        rows: [
          ["Model of reality, {M}", "Each buyer and seller evaluates the quoted candidate price."],
          ["Perceived feasible set, {F̂}", "Buyers can choose to buy or not buy. Sellers can choose to sell or not sell."],
          ["Valuation, {V}", "Buyers compare the price with their willingness to pay. Sellers compare it with their costs."],
          ["Decision process, {D}", "Select the higher valued option. Participate when the values are equal."],
          ["Selected action, {C}", "Each buyer chooses whether to buy, and each seller chooses whether to sell."],
        ],
      },
      note: "The model compares decisions at different quoted prices, then repeats the comparison with an additional buyer or seller.",
    },
    takeaway: [
      "The same quoted price can lead to different choices because buyers have different willingness to pay and sellers have different costs. {M} supplies the price used in valuation, and {D} selects each agent’s action.",
      "Counting those selected actions gives quantity demanded and quantity supplied. A clearing price makes the counts equal. This example does not model completed transactions or a process that adjusts prices over time.",
    ],
    formalModel: {
      introduction: "This example applies TER Model 5.1, the Agent Decision Model, separately to each buyer and seller.",
      explanation: [
        "For a buyer, {V} assigns buying the willingness to pay minus the quoted price. For a seller, {V} assigns selling the quoted price minus the selling cost. Not participating has value 0.",
        "{D} selects the option with the higher value, with ties configured to favor participation. Each candidate price supplies a different price in {M}; the valuation rules and decision process remain the same.",
        "The test counts the selected actions to identify prices where quantity demanded equals quantity supplied. That counting is an analysis of {C}, not a reality function {R} or a realized outcome {O}.",
      ],
      closing: "The reported clearing prices describe the tested price grid and agent configurations.",
    },
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
    modelDetails: [
      "Each buyer or seller decides whether to participate for one unit at the quoted price.",
      "The example evaluates candidate prices from 1 to 9. It does not simulate an auction, bargaining, or price adjustment.",
      "When participating and not participating have equal value, the agent participates.",
      "The changes from adding a buyer or seller are results for these specified cases, not a claim that every market has the same response.",
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
    referenceResults: {
      heading: "Original market checks",
      table: {
        columns: ["Candidate price", "Excess demand"],
        rows: [
          ["4", "Positive"],
          ["5", "Zero — market clears"],
          ["6", "Negative"],
        ],
      },
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
    introduction: [
      "Would you sell a good car for a price based on cars of mixed quality?",
      "Six sellers each own a car: three are high quality and three are low quality. Each seller knows its own car’s quality.",
      "When quality cannot be verified, every seller receives the same offer based on the believed share of high quality cars. When quality is verified, offers reflect each car’s quality.",
    ],
    activityHeading: "Try it",
    instruction:
      "Start with pooled pricing and a believed high quality share of 0.5 (50%). Run the example, then switch to verified pricing and run again. Which sellers change their choice?",
    configuration: {
      table: {
        columns: ["Component", "Role in this example"],
        rows: [
          [
            "Model of reality, {M}",
            "Each seller observes an offered price. Pooled pricing uses the believed quality mix; verified pricing uses each car’s quality.",
          ],
          ["Valuation, {V}", "Compare the offered price with the seller’s reservation value."],
          ["Decision process, {D}", "Sell when the offer meets or exceeds the reservation value; otherwise hold."],
          ["Selected action, {C}", "Each seller chooses to sell or hold."],
          ["Reality function, {R}", "Use all six selected actions and actual car qualities to count sales."],
          ["System outcome, {O_t}", "Cars sold by actual quality, and the total sold."],
        ],
      },
      note: "Changing the pricing information changes {M}. Actual car quality, reservation values, and the valuation and decision rules stay fixed.",
    },
    takeaway: [
      "The sellers’ cars and reservation values stay the same, but different pricing information in {M} can change how {V} evaluates selling. The same decision rule {D} can then select different actions {C}.",
      "The pooled result depends on the believed quality mix. High quality sellers sell once the pooled offer reaches 8. {R} counts the cars sold using their actual qualities, not the belief used to set the offer.",
    ],
    formalModel: {
      introduction: "This example uses TER Model 5.1 for each seller’s decision and Model 5.3 for the joint system outcome.",
      explanation: [
        "Under pooled pricing, every seller observes the same offer: the believed high quality share multiplied by 10, plus the remaining share multiplied by 4. Under verified pricing, high quality sellers observe 10 and low quality sellers observe 4.",
        "{V} evaluates selling as the observed offer minus the seller’s reservation value. Holding has value 0. {D} selects the higher value, with ties configured to favor selling.",
        "All six selected actions enter one joint {R}. It reads actual quality and reports sales counts in {O_t}. No separate seller-level outcomes are defined.",
      ],
      closing: "The price is supplied by the scenario. Buyers are not modeled as separate deciding agents.",
    },
    scope:
      "One decision point, six interacting sellers. This illustrates TER Models 5.1 and 5.3, not real used-car markets.",
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
          "The reality rule reads each car's actual quality, a scenario-specified condition that represents one relevant aspect of {F_t}. It is not a complete representation of F_t.",
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
          "How many high-quality and low-quality cars are sold, and the total, returned by the simulator. No seller-level outcomes {O_i,t} are defined.",
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
    // The 50% configuration only, not every pooled run.
    referenceResults: {
      heading: "Default comparison",
      intro: "These checks use pooled pricing with a believed high quality share of 0.5 and compare it with verified pricing.",
      table: {
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
      checks: [
        "Under pooled, asymmetric-information pricing, high-quality sellers withhold their goods from the market.",
        "Under pooled pricing, low-quality sellers still sell.",
        "This produces adverse selection: only low-quality goods trade under pooled pricing.",
        "Under verified, symmetric-information pricing, both high-quality and low-quality goods trade.",
        "The same sellers, with the same reservation values and perceived feasible sets, decide differently when the offered price changes from the pooled price to the verified price.",
        "Gains from trade exist for high-quality sellers, but go unrealized under asymmetric information.",
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
    introduction: [
      "What if a decision benefits a business but creates a larger cost for others?",
      "Producing gives a firm a benefit of 4 and imposes a cost of 7 on others. Not producing gives neither benefit nor cost. Compare the firm’s choice when it counts only its own benefit with its choice when it also counts the external cost.",
    ],
    activityHeading: "Worked example",
    workedExample: {
      table: {
        columns: ["Metric", "Counts its own benefit", "Also counts the external cost"],
        rows: [
          ["Value assigned to producing", "4", "−3"],
          ["Value assigned to not producing", "0", "0"],
          ["Selected action", "Produce", "Do not produce"],
        ],
      },
    },
    configuration: {
      table: {
        columns: ["Component", "Role in this example"],
        rows: [
          ["Model of reality, {M}", "The firm has the same information about the external effect in both cases."],
          ["Valuation, {V}", "Count only the firm’s benefit, or include the external cost as well."],
          ["Decision process, {D}", "Select the action with the higher value."],
          ["Selected action, {C}", "Produce or do not produce."],
          ["Reality function, {R}", "Report the private value and external effect associated with the selected action."],
          ["Realized outcome, {O}", "The private value, external effect, and their sum under this example’s measure."],
        ],
      },
      note: "The comparison changes how {V} accounts for the external effect. The firm’s information and the scenario’s actual values stay the same.",
    },
    takeaway: [
      "Knowing about a cost and including it in a decision are different things. Here, {M} contains the same information in both cases, but {V} combines that information differently.",
      "That change in valuation changes {C}. {R} then reports the consequences of the selected action using the same underlying scenario data.",
    ],
    formalModel: {
      introduction: "This example uses TER Model 5.1 to select an action and Model 5.2 to represent its realized outcome.",
      outcomeModel: true,
      explanation: [
        "Producing has private value 4 and external effect −7. Not producing has private value 0 and external effect 0.",
        "In the first case, {V} counts only private value. In the second, {V} adds the external effect, so producing is valued at −3. {D} selects the higher valued action in each case.",
        "{R} uses the selected action and the scenario’s actual values to report the outcome. The reported combined value is private value plus external effect, a measure specified for this example.",
      ],
      closing: "The external cost is represented numerically; the affected party is not modeled as a separate deciding agent.",
    },
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
          "The reality rule reads the scenario's actual private values and external effects for each action. These are scenario-specified conditions that represent relevant aspects of {F_t}, not a complete representation of it.",
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
        key: "R",
        symbol: "R",
        name: "Reality function",
        definition:
          "Maps the selected action(s) and the relevant objectively realized state F_t to the realized outcome; its arguments depend on model scope.",
        mapping:
          "Uses the selected action and the scenario’s actual private values and external effects to report the outcome.",
        testTreatment: "Fixed",
      },
      {
        key: "O",
        symbol: "O",
        name: "Realized outcome",
        definition: "Realized outcome associated with the selected action.",
        mapping:
          "The reality rule takes the selected action and the scenario's own private-value and external-effect data and reports {O_i,t}: the private value, the external effect, and this test's specified social value, defined here as private value plus external effect. This is a single-agent specification, so no system outcome {O_t} is defined.",
        testTreatment: "Result",
      },
    ],
    modelDetails: [
      "The firm’s information about the external effect matches the scenario’s actual external effect in both cases.",
      "The example changes valuation directly. It does not model a tax, regulation, liability rule, bargaining process, or other mechanism that would bring about that change.",
      "Adding private value and external effect defines the combined value used here. It is not a universal TER welfare rule.",
      "This is one firm making one decision. There is no separate system outcome {O_t}.",
    ],
    hypotheses: [
      "Producing is privately profitable.",
      "Producing creates a negative external effect.",
      "Private value can be positive while the specified social value is negative.",
      "The privately selected action can have lower specified social value than the available alternative.",
      "Including the external effect in the firm's own valuation can change the selected action.",
    ],
    sourcePath: "research/tests/test_08_externalities.py",
  },
  {
    slug: "actual-vs-perceived-feasibility",
    title: "Perceived Feasibility vs. Scenario Permission",
    category: "Feasibility",
    summary:
      "A producer may select an action the scenario does not permit. The selected action stays the one the decision process chose; the realized outcome shows what the scenario allowed.",
    sourceLabel: "Model 5.2",
    introduction: [
      "Choosing an action does not guarantee it can be carried out.",
      "Three producers consider making nothing, 60 units, or 100 units. Each assigns those options scores of 0, 6, and 10 and chooses the highest score among the options it perceives.",
      "The producers differ in what they believe they can attempt and what the scenario permits. In this example, production is capped at the largest permitted quantity.",
    ],
    activityHeading: "Worked example",
    workedExample: {
      table: {
        columns: ["Producer", "Permitted production", "Perceived options", "Selected action", "Actual production"],
        rows: [
          ["Accurate perception", "0 or 60 units", "0 or 60 units", "Produce 60 units", "60 units"],
          ["Mistaken perception", "0 or 60 units", "0, 60, or 100 units", "Produce 100 units", "60 units"],
          ["Severe mismatch", "0 units", "0, 60, or 100 units", "Produce 100 units", "0 units"],
        ],
      },
    },
    configuration: {
      table: {
        columns: ["Component", "Role in this example"],
        rows: [
          ["Perceived feasible set, {F̂}", "The production options each producer believes it can attempt."],
          ["Valuation, {V}", "Produce nothing scores 0, produce 60 scores 6, and produce 100 scores 10."],
          ["Decision process, {D}", "Select the highest score among the perceived options."],
          ["Selected action, {C}", "The production action selected before realization."],
          ["Objective feasible state of reality, {F_t}", "Represented here through the scenario’s production permissions."],
          ["Reality function, {R}", "Cap production at the largest permitted quantity."],
          ["Realized outcome, {O}", "The quantity actually produced under that rule."],
        ],
      },
      note: "The comparison varies perceived options and production permissions. The scores and decision rule stay the same.",
    },
    takeaway: [
      "{D} selects from {F̂}, so a producer can choose an action that the scenario does not permit it to complete. The selected action {C} and realized outcome {O} answer different questions: what was chosen, and what happened?",
      "Here, {R} caps production without changing the recorded choice. A selection of 100 units can therefore be followed by production of 60 units or none.",
    ],
    formalModel: {
      introduction: "This example uses TER Model 5.1 for action selection and Model 5.2 for outcome realization.",
      outcomeModel: true,
      explanation: [
        "Each producer uses the same action scores and decision rule. Differences in {F̂} determine which actions {D} can select.",
        "The scenario’s permission data represents a production constraint relevant to {F_t}. {R} reads that data after action selection and caps the realized quantity at the largest permitted quantity.",
        "{R} does not run {D} again or replace {C} with a different selected action. The realized quantity is reported in {O}.",
      ],
      closing: "This example specifies a particular response to an attempted action that cannot be fully carried out.",
    },
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
          "The scenario's permission data lists the permitted actions for each producer: hold or produce 60 for the accurate and mistaken producers, hold only for the severely mismatched producer. This data represents the relevant constraint (a production ceiling) in this implementation; it is not {F_t} itself. It is indexed by producer for convenience, but {F_t} is not agent specific, and only the reality rule reads it.",
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
          "Each producer compares its perceived feasible actions and selects the highest-valued one. This comparison only ever considers F̂ — it never checks {F_t}.",
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
        key: "R",
        symbol: "R",
        name: "Reality function",
        definition:
          "Maps the selected action(s) and the relevant objectively realized state F_t to the realized outcome; its arguments depend on model scope.",
        mapping:
          "Caps the selected production quantity at the largest quantity permitted for that producer by the scenario.",
        testTreatment: "Fixed rule",
      },
      {
        key: "O",
        symbol: "O",
        name: "Realized outcome",
        definition: "Realized outcome associated with the selected action.",
        mapping:
          "Realized production, {O_i,t}, once the already-selected action meets the scenario's permission data: 60 units for the accurate producer, 60 units for the mistaken producer (capped down from the 100 it selected), and 0 units for the severely mismatched producer. This is an agent-level specification (Model 5.2); no system outcome {O_t} is defined. This test's own reality rule never re-runs the decision process or valuation — it only measures how much of the already-selected action the permission data allows. Implementation: capacity_constrained_realization.",
        testTreatment: "Result",
      },
    ],
    modelDetails: [
      "This is a framework example of outcome realization, not a reproduction of a separate economic theory.",
      "Production permissions are stored by producer for this implementation. They represent relevant constraints within {F_t}; they do not make {F_t} agent specific.",
      "Capping production is this example’s reality rule. Other scenarios can specify failure, different partial outcomes, or other consequences.",
      "The selected action remains recorded as chosen. No learning or feedback occurs in this single decision period.",
    ],
    hypotheses: [
      "When a producer's perceived feasible set matches the actions the scenario permits, the selected action is fully realized.",
      "When the selected action is perceived feasible but not permitted by the scenario, the realized outcome may be a partial realization of that action, capped by the permission data.",
      "In the current framework, the selected action is recorded as chosen; only the realized outcome differs from what was selected.",
      "Under this test's specific reality rule, a more severe mismatch between F̂ and the permission data can produce a larger shortfall — but this is not asserted as a universal consequence of a selected action not being permitted.",
    ],
    implementationMapping: [
      { label: "objective", value: "G" },
      { label: "model_of_reality", value: "M (empty)" },
      { label: "perceived_feasible_set", value: "F̂" },
      { label: "valuation, read by mapped_value", value: "V" },
      { label: "horizon", value: "H" },
      { label: "decision_process = maximize_value", value: "D" },
      { label: "initial_state[\"permitted_actions\"]", value: "Aspect of F_t (permission data)" },
      { label: "reality = capacity_constrained_realization", value: "R" },
      { label: "realized_units", value: "O_{i,t}" },
    ],
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
    introduction: [
      "Can discovering an overlooked option change the next decision?",
      "An agent can take an ordinary action or a better alternative, but initially perceives only the ordinary action. Their scores stay fixed at 4 and 9.",
      "The example includes a specific learning rule: after the agent experiences the ordinary action, the rule adds the alternative to its perceived options.",
    ],
    activityHeading: "Worked example",
    instruction: "Compare the options the agent perceives before each decision with the action it selects.",
    configuration: {
      table: {
        columns: ["Component", "Role in this example"],
        rows: [
          [
            "Perceived feasible set, {F̂}",
            "Initially contains only the ordinary action. The update adds the alternative before the next decision.",
          ],
          ["Valuation, {V}", "The ordinary action scores 4 and the alternative scores 9."],
          ["Decision process, {D}", "Select the highest score among the perceived options."],
          ["Selected action, {C}", "The action selected at each decision point."],
          ["Realized outcome, {O}", "The action the agent experiences and observes."],
        ],
      },
      note: "Both actions remain permitted. The specified learning rule updates {F̂} after the first outcome; the scores and decision process stay fixed.",
    },
    takeaway: [
      "An option can be permitted without appearing in {F̂}. The first decision cannot select the alternative because the agent does not yet perceive it as available.",
      "After the specified update adds that option, the same {V} and {D} select it at the next decision. The changed choice comes from an expanded perceived feasible set, not a higher score or a different decision rule.",
    ],
    formalModel: {
      introduction:
        "This example combines action selection in TER Model 5.1, outcome realization in Model 5.2, and the feedback structure described in Model 5.5.",
      outcomeModel: true,
      explanation: [
        "At the first decision, {F̂} contains only the ordinary action. {D} selects it, and {R} records that action as the agent’s experienced outcome.",
        "The agent observes its own outcome. The configured update rule then adds the alternative to {F̂} before the second decision, where {D} compares the unchanged scores of 4 and 9.",
        "Model 5.5 describes possible feedback into later conditions. This single-agent example starts that feedback from {O_i,t} and updates only {F̂}.",
      ],
      closing: "The discovery is supplied by the configured update rule. The example does not explain why the alternative was initially overlooked.",
    },
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
        mapping: "Empty and fixed. Neither the valuation rule nor the decision process uses M in this example.",
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
    modelDetails: [
      "One agent makes two decisions. Both actions are permitted throughout, and their scores remain 4 and 9.",
      "The agent observes its own realized outcome exactly, and nothing else.",
      "After observing the ordinary action, the update rule adds the alternative to the perceived feasible set. The rule reads the agent’s state and observation, not {F_t}.",
      "{R} records the experienced action. It does not check action permissions or introduce additional consequences.",
      "TER does not require experience to reveal better options or improve later decisions.",
      // Preserved verbatim from the earlier assumptions; not covered above.
      "Values are scenario-specific assumptions, not TER primitives.",
    ],
    hypotheses: [
      "Premise check: the better action is permitted but not initially perceived.",
      "The first decision is restricted to the ordinary action.",
      "The observed outcome of that decision leads the update to add the better action to F̂ for the next decision.",
      "The next decision selects the better action, now perceived and more highly valued.",
      "The objectively permitted actions do not change during the run; only perception does.",
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
    sourcePath: "research/scenarios/feasible_set_learning.py",
    testPath: "research/tests/test_22_feasible_set_learning.py",
  },
];

export function getScenario(slug: string): Scenario | undefined {
  return scenarios.find((scenario) => scenario.slug === slug);
}
