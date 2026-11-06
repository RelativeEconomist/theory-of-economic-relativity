/**
 * Presentation metadata for the Krugman (1980) reproduction, Configuration K.
 *
 * This file does not define or reinterpret TER or Krugman. Text mirrors
 * research/reproductions/krugman_1980_configuration.md and
 * krugman_1980_validation.md; the executable behavior lives in
 * krugman_1980.py, krugman_1980_ter.py, and their tests. If this file and
 * those sources ever disagree, the research sources win.
 */

import type { ScenarioField, TerComponentMapping } from "../learn/scenarios";

const REPO_BLOB = "https://github.com/RelativeEconomist/theory-of-economic-relativity/blob/main/";

export interface ReproductionLink {
  label: string;
  path: string;
  href: string;
}

const link = (label: string, path: string): ReproductionLink => ({ label, path, href: `${REPO_BLOB}${path}` });

export const krugman1980 = {
  slug: "krugman-1980",
  title: "Krugman (1980): Trade and Product Variety",
  status: "In verification",
  summary: "A TER reproduction of Section I, comparing closed economies with trade without transport costs.",
  evidence:
    "Implemented with 43 passing tests. Results match the project’s mathematical benchmark at the tested parameters. Broader parameter checks and independent review remain open.",

  paper: {
    citation:
      "Paul Krugman, “Scale Economies, Product Differentiation, and the Pattern of Trade,” American Economic Review 70(5), 1980.",
    scope:
      "Section I only: two closed economies, then the same two economies integrated by trade with zero transport costs. Later sections of the paper are not reproduced.",
    question:
      "Can Krugman’s Section I model be represented as a TER configuration without changing either Krugman’s economics or TER’s definitions?",
  },

  /** Krugman's Section I assumptions, in priority order (first four stay visible). */
  assumptions: [
    "Consumers have identical symmetric preferences U = Σ c_i^θ, with 0 < θ < 1.",
    "Producing x units of a variety takes α + βx units of labor; labor is the only factor of production.",
    "Each active firm produces one variety. Product differentiation is costless.",
    "Free entry, under a large-number approximation: firms take aggregate market conditions as given.",
    "Consumers within each country are identical.",
    "Under trade, the two countries have identical preferences and technologies.",
    "Under trade, transport costs are zero.",
    "Autarky and integrated trade are separate configurations, not periods of an adjustment path.",
  ],

  /** Configuration K on Model 5.1 and Model 5.3. Consumers and active firms share each row. */
  terComponents: [
    {
      key: "G",
      symbol: "G",
      name: "Objective",
      definition: "Result or condition that provides the reference for valuation when valuation is used.",
      mapping: "Consumer: maximize utility from consumption. Firm: maximize profit.",
      testTreatment: "Agent behavior",
    },
    {
      key: "M",
      symbol: "M",
      name: "Model of reality",
      definition:
        "The agent's model of reality, including information, beliefs, assumptions, expectations, and interpretations.",
      mapping:
        "Consumer: prices, income, and available varieties. Firm: perceived demand, wage, market size, its own technology, and the large-number environment. Every agent expects the price derived from the TER firm decision; no agent observes another agent’s selected action.",
      testTreatment: "Agent behavior",
    },
    {
      key: "F_hat",
      symbol: "F̂",
      name: "Perceived feasible set",
      definition: "Actions the agent perceives as available to attempt.",
      mapping: "Consumer: bundles within its perceived budget. Firm: all positive prices.",
      testTreatment: "Agent behavior",
    },
    {
      key: "V",
      symbol: "V",
      name: "Valuation",
      definition: "Valuation of actions relative to the agent's objective.",
      mapping: "Consumer: Krugman’s utility U = Σ c_i^θ. Firm: expected profit under its model of demand and costs.",
      testTreatment: "Agent behavior",
    },
    {
      key: "H",
      symbol: "H",
      name: "Time horizon",
      definition: "Which future consequences the agent considers relevant to valuation.",
      mapping: "The current static decision. Section I has no intertemporal problem.",
      testTreatment: "Agent behavior",
    },
    {
      key: "D",
      symbol: "D",
      name: "Decision process",
      definition:
        "Process through which the agent selects among perceived feasible actions. It may condition directly on the model of reality and may use valuation when applicable.",
      mapping:
        "Consumer: closed-form maximizer of its V, verified against V by test. Firm: numerical search for the price that maximizes its expected profit.",
      testTreatment: "Agent behavior",
    },
    {
      key: "C",
      symbol: "C",
      name: "Selected action",
      definition: "Action selected by the agent.",
      mapping: "Consumer: a consumption bundle. Firm: a price, which gives the markup p/w.",
      testTreatment: "TER decision",
    },
    {
      key: "F",
      symbol: "F_t",
      name: "Objective feasible state of reality",
      definition:
        "The objectively realized conditions and constraints relevant when the selected action(s) at decision point t are realized. Not agent specific, and not an input to the decision process.",
      mapping:
        "Labor forces L and L*, the actual technology α + βx, and whether the countries are in autarky or integrated trade with zero transport costs.",
      testTreatment: "Configuration input",
    },
    {
      key: "R",
      symbol: "R",
      name: "Reality function",
      definition:
        "Maps the selected action(s) and the relevant objectively realized state F_t to the realized outcome; its arguments depend on model scope.",
      mapping:
        "One joint R per scenario. It realizes the allocation only if F_t permits all of it; otherwise it reports the allocation infeasible and realizes nothing. It never rewrites a selected action.",
      testTreatment: "Realization",
    },
    {
      key: "O",
      symbol: "O_t",
      name: "System outcome",
      definition: "Realized system outcome produced by interacting selected actions encountering F_t.",
      mapping:
        "Consumption, sales, output, labor used, revenue, cost, profit, expenditure, and trade flows. Utility is each consumer’s own V evaluated at its realized consumption.",
      testTreatment: "Realized outcome",
    },
  ] satisfies TerComponentMapping[],

  /** How Configuration K obtains Krugman's equilibrium, in dependency order. */
  derivation: [
    "Markup (TER decision). One configured firm runs through TER and selects its price. Its decision does not depend on the market level it expects (tested), and a firm holding the derived beliefs selects the same price.",
    "Output per firm (zero profit). From m·w·x = w(α + βx), x = α/(m − β).",
    "Firm count (full employment). From n(α + βx) = L, n = L/(α + βx).",
    "Equal wages (world goods-market clearing). With CES demand, clearing holds only at w = w*.",
  ],

  modelingChoices: [
    "Krugman’s equilibrium requires mutually consistent expectations, so agents expect the price derived from the TER firm decision. That selected prices equal it confirms a fixed point; it is not independent evidence.",
    "Zero profit, full employment, and goods-market clearing are Krugman’s equilibrium conditions. They are used in the derivation, and TER confirms that its joint R realizes them. That tests the implementation, not the conditions.",
    "One consumer agent per country stands for its L identical consumers; R scales the per-capita bundle by L.",
    "Firms produce what is purchased at their selected price, so unsold output cannot occur. Krugman specifies no rationing rule, so none is invented.",
    "Only the ordinal welfare comparison is validated, not a cardinal welfare magnitude.",
  ],

  /** Krugman's Section I results, how the TER execution obtains each, and the benchmark value. */
  resultsTable: {
    columns: ["Krugman result", "How TER obtains it", "Benchmark at the fixtures"],
    rows: [
      ["Markup p/w = β/θ", "TER agent decision", "0.6667"],
      ["Output per firm x = αθ / [β(1 − θ)]", "Derived by zero profit; realized output matches", "12"],
      ["Varieties n = L(1 − θ)/α", "Derived by full employment", "Home 10, foreign 5"],
      ["Zero profit, full employment, market clearing", "Equilibrium conditions; realization checks", "Hold"],
      ["No profitable entry", "Equilibrium condition; checked with an active firm’s own V", "Holds"],
      ["Equal wages under trade", "Derived from world goods-market clearing", "w = w*"],
      ["Trade shares", "Realized from consumer decisions", "Home imports 1/3, foreign imports 2/3"],
      ["Balanced trade", "Equilibrium condition; realization check", "26.67 each way, in wage units"],
      ["Gains from variety", "Realized utility under each consumer’s V; ordinal only", "Both countries gain"],
    ],
  },

  fixtures: [
    { label: "Home labor L", value: "80" },
    { label: "Foreign labor L*", value: "40" },
    { label: "Fixed labor requirement α", value: "2" },
    { label: "Marginal labor requirement β", value: "0.5" },
    { label: "Preference parameter θ", value: "0.75" },
    { label: "Wage numeraire w", value: "1" },
  ] satisfies ScenarioField[],

  testSuites: [
    {
      label: "Analytical benchmark",
      count: 8,
      description:
        "Krugman’s closed-form solution, without TER: markup, zero profit, full employment, variety counts, unchanged output under trade, equal wages, trade shares and balance, and gains from variety.",
    },
    {
      label: "TER execution",
      count: 35,
      description:
        "Configuration K run through TER Core: execution boundaries, the firm and consumer decisions, the equilibrium and realization checks, the trade and welfare results, and the cases that must fail.",
    },
  ],

  /** Checks that can fail, from the validation document. */
  failureChecks: [
    "Firms that misperceive demand elasticity do not reproduce Krugman’s markup, and R reports their allocation infeasible.",
    "Counterfactual prices consumers cannot pay, labor demand beyond the labor force, purchases of unoffered varieties, negative purchases, and nonpositive prices are each reported infeasible, with nothing realized.",
    "A firm price that is not a fixed point, or a firm count that is not a whole number, raises an error instead of being adjusted.",
  ],

  openTasks: [
    "Broader parameter checks. The full equilibrium is checked at one illustrative fixture set and under wage rescaling; the firm and consumer decisions are also checked at θ = 0.99.",
    "Independent review of the configuration, the mappings, and the tests.",
  ],

  limitations: [
    "Firms are agents, so the firm count n must be a whole number. Krugman treats n as continuous, and fixtures where n is not whole are rejected.",
    "Consumers choose quantities from expected prices, so counterfactuals away from equilibrium do not represent Krugman’s demand response.",
    "Infeasible allocations are reported, not resolved. Without a rationing rule, Configuration K says nothing about what would be realized instead.",
    "Potential entrants are not modeled. “No profitable entry” is checked with an active firm’s own V, which an identical entrant would share under the large-number approximation.",
    "The equilibrium conditions themselves are not tested, and the single-pass fixed point relies on the markup not depending on expected market conditions.",
    "Passing Configuration K does not validate TER as a general theory. It shows that this established model can be represented, and its predicted relationships reproduced, within the TER architecture.",
  ],

  links: [
    link("Analytical benchmark", "research/reproductions/krugman_1980.py"),
    link("TER configuration", "research/reproductions/krugman_1980_ter.py"),
    link("Benchmark tests", "research/reproductions/test_krugman_1980.py"),
    link("TER execution tests", "research/reproductions/test_krugman_1980_ter.py"),
    link("Configuration document", "research/reproductions/krugman_1980_configuration.md"),
    link("Validation document", "research/reproductions/krugman_1980_validation.md"),
  ],
};

/** Reproductions listed on /learn/, in display order. */
export const reproductions = [krugman1980];
