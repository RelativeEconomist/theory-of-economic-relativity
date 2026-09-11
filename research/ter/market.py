from dataclasses import dataclass

from research.ter.decision import select_action
from research.ter.runner import build_agent
from research.ter.scenario import AgentSpec


@dataclass(frozen=True)
class MarketState:
    """
    Aggregate market state at a quoted price.

    demand   -> number of buyers selecting "buy"
    supply   -> number of sellers selecting "sell"
    """
    price: float
    demand: int
    supply: int

    @property
    def excess_demand(self) -> int:
        return self.demand - self.supply


def evaluate_market(
    buyers: list[AgentSpec],
    sellers: list[AgentSpec],
    price: float,
) -> MarketState:
    """
    Evaluate decentralized agent decisions at a given market price.

    Price becomes part of each agent's model of reality M. Agents are
    built fresh from their declarative AgentSpec for this price, so
    nothing about a previous price evaluation can leak into this one.

    Each agent then selects an action through the standard TER
    decision process:

        C_i = D_i(F_hat_i, G_i, M_i, V_i, H_i)

    The market aggregates the resulting actions.
    """
    demand = 0
    supply = 0

    for buyer_spec in buyers:
        buyer = build_agent(buyer_spec)
        buyer.model_of_reality["price"] = price

        if select_action(buyer) == "buy":
            demand += 1

    for seller_spec in sellers:
        seller = build_agent(seller_spec)
        seller.model_of_reality["price"] = price

        if select_action(seller) == "sell":
            supply += 1

    return MarketState(
        price=price,
        demand=demand,
        supply=supply,
    )


def find_market_clearing_states(
    buyers: list[AgentSpec],
    sellers: list[AgentSpec],
    prices: list[float],
) -> list[MarketState]:
    """
    Return quoted prices where aggregate quantity demanded equals
    aggregate quantity supplied.

    This is a discrete market-clearing test, not a claim that all real
    markets continuously or instantaneously clear.
    """
    states = [
        evaluate_market(
            buyers=buyers,
            sellers=sellers,
            price=price,
        )
        for price in prices
    ]

    return [
        state
        for state in states
        if state.demand == state.supply
    ]
