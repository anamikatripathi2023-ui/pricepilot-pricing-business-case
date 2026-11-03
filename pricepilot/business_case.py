"""36-month business case for FreshKart Plus, with Monte Carlo risk analysis.

Per member, per month:

    contribution = price
                 + extra orders x contribution per order      (members order more)
                 - all member orders x fees waived per order   (the cost of "free delivery")

Members ramp up along an S-curve to a steady state (eligible users x take rate x
awareness). Churned members must be replaced, and every new member costs CAC.
"""
from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np
import pandas as pd

from .pricing import DemandCurve

CRORE = 1e7
LAKH = 1e5


@dataclass(frozen=True)
class Assumptions:
    price: float = 99.0                          # Rs per month
    eligible_users: int = 900_000                # monthly customers ordering 2+ times a month
    awareness: float = 0.80                      # share of eligible users who ever see the offer
    baseline_orders: float = 4.0                 # orders/month a typical joiner already places
    incremental_orders: float = 1.2              # extra orders/month once a member
    contribution_per_order: float = 45.0         # Rs margin per order after product and delivery cost
    fees_waived_per_order: float = 18.0          # Rs delivery + handling fees no longer charged
    monthly_churn: float = 0.06
    cac: float = 150.0                           # Rs marketing cost per new member
    build_cost: float = 1.5 * CRORE              # one-off product and engineering cost
    monthly_fixed_cost: float = 8 * LAKH         # support, partnerships, ops
    months: int = 36
    ramp_midpoint: float = 6.0                   # month when adoption reaches half of steady state
    annual_discount_rate: float = 0.12
    intent_calibration: float = 1.0              # multiplier on survey take rates (1.0 = as calibrated)


def unit_economics(a: Assumptions) -> dict:
    """Monthly contribution from one member, before acquisition cost."""
    extra = a.incremental_orders * a.contribution_per_order
    waived = (a.baseline_orders + a.incremental_orders) * a.fees_waived_per_order
    per_member = a.price + extra - waived
    payback = a.cac / per_member if per_member > 0 else float("inf")
    lifetime_months = 1 / a.monthly_churn
    return {"subscription": a.price, "extra_order_margin": extra, "fees_waived": -waived,
            "contribution_per_member": per_member, "cac_payback_months": payback,
            "ltv": per_member * lifetime_months, "ltv_to_cac": per_member * lifetime_months / a.cac}


def _membership(a: Assumptions, demand: DemandCurve) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(months, members, new members): S-curve to steady state; churned members are replaced."""
    take_rate = float(demand.take_rate(a.price)) * a.intent_calibration
    steady_state = a.eligible_users * a.awareness * min(take_rate, 1.0)
    months = np.arange(0, a.months + 1)
    adoption = np.where(months == 0, 0.0, 1 / (1 + np.exp(-(months - a.ramp_midpoint) / 1.5)))
    members = steady_state * adoption
    previous = np.concatenate([[0.0], members[:-1]])
    new_members = np.maximum(members - previous * (1 - a.monthly_churn), 0)
    return months, members, new_members


def npv(a: Assumptions, demand: DemandCurve) -> float:
    """NPV only, without building the P&L table: fast enough for thousands of simulations."""
    months, members, new_members = _membership(a, demand)
    net = (members * unit_economics(a)["contribution_per_member"] - new_members * a.cac
           + np.where(months == 0, -a.build_cost, -a.monthly_fixed_cost))
    monthly_rate = (1 + a.annual_discount_rate) ** (1 / 12) - 1
    return float((net / (1 + monthly_rate) ** months).sum())


def project(a: Assumptions, demand: DemandCurve) -> pd.DataFrame:
    """Month-by-month members and P&L in rupees. Month 0 is the build month."""
    months, members, new_members = _membership(a, demand)
    unit = unit_economics(a)
    pnl = pd.DataFrame({
        "month": months,
        "members": members.round(),
        "new_members": new_members.round(),
        "subscription_revenue": members * a.price,
        "extra_order_margin": members * unit["extra_order_margin"],
        "fees_waived": members * unit["fees_waived"],
        "acquisition_cost": -new_members * a.cac,
        "fixed_cost": np.where(months == 0, -a.build_cost, -a.monthly_fixed_cost),
    })
    money = pnl.columns.drop(["month", "members", "new_members"])
    pnl[money] = pnl[money] + 0.0                          # turn -0.0 into 0.0 for clean exports
    pnl["net"] = pnl[["subscription_revenue", "extra_order_margin", "fees_waived", "acquisition_cost",
                      "fixed_cost"]].sum(axis=1)
    pnl["cumulative"] = pnl["net"].cumsum()
    return pnl


def summarise(pnl: pd.DataFrame, a: Assumptions) -> dict:
    monthly_rate = (1 + a.annual_discount_rate) ** (1 / 12) - 1
    npv = float((pnl["net"] / (1 + monthly_rate) ** pnl["month"]).sum())
    positive = pnl.index[pnl["cumulative"] >= 0]
    return {
        "npv": npv,
        "payback_month": int(pnl.loc[positive[0], "month"]) if len(positive) else None,
        "steady_state_members": float(pnl["members"].iloc[-1]),
        "year3_net": float(pnl[pnl["month"] > a.months - 12]["net"].sum()),
        "total_net": float(pnl["net"].sum()),
    }


def price_sweep(a: Assumptions, demand: DemandCurve, prices=range(29, 250, 5)) -> pd.DataFrame:
    """NPV, members and unit contribution at each candidate price."""
    rows = []
    for price in prices:
        scenario = replace(a, price=float(price))
        result = summarise(project(scenario, demand), scenario)
        rows.append({"price": price, "take_rate": float(demand.take_rate(price)) * a.intent_calibration,
                     "members": result["steady_state_members"], "npv": result["npv"],
                     "contribution_per_member": unit_economics(scenario)["contribution_per_member"]})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- risk
# (low, most likely, high) for the inputs we are least sure about.
UNCERTAIN_INPUTS = {
    "intent_calibration": (0.6, 1.0, 1.2),
    "incremental_orders": (0.5, 1.2, 1.8),
    "fees_waived_per_order": (12.0, 18.0, 26.0),
    "monthly_churn": (0.04, 0.06, 0.10),
    "cac": (80.0, 150.0, 250.0),
}


def monte_carlo(a: Assumptions, demand: DemandCurve, runs: int = 5000, seed: int = 3) -> pd.DataFrame:
    """Sample the uncertain inputs from triangular distributions and record NPV for each run."""
    rng = np.random.default_rng(seed)
    draws = {name: rng.triangular(low, mode, high, runs) for name, (low, mode, high) in UNCERTAIN_INPUTS.items()}
    npvs = [npv(replace(a, **{name: float(values[i]) for name, values in draws.items()}), demand)
            for i in range(runs)]
    return pd.DataFrame(draws).assign(npv=npvs)


def tornado(a: Assumptions, demand: DemandCurve) -> pd.DataFrame:
    """NPV when each uncertain input is moved to its low and high value, others at base."""
    base = npv(a, demand)
    rows = []
    for name, (low, _, high) in UNCERTAIN_INPUTS.items():
        npv_low, npv_high = npv(replace(a, **{name: low}), demand), npv(replace(a, **{name: high}), demand)
        rows.append({"input": name, "low_value": low, "high_value": high, "npv_at_low": npv_low,
                     "npv_at_high": npv_high, "swing": abs(npv_high - npv_low), "base_npv": base})
    return pd.DataFrame(rows).sort_values("swing", ascending=False).reset_index(drop=True)
