"""Combine survey, demand and business case into a pricing recommendation.

Run from the project root:
    python -m pricepilot.recommend --out outputs/pricing_recommendation.md
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np
import pandas as pd

from .business_case import (CRORE, Assumptions, monte_carlo, npv, price_sweep, project, summarise, tornado,
                            unit_economics)
from .pricing import (DemandCurve, VanWestendorp, fit_demand, stated_take_rates, validate_survey, van_westendorp,
                      van_westendorp_by_segment)

SAMPLE_SURVEY = Path(__file__).resolve().parent.parent / "data" / "pricing_survey.csv"
CHARM_PRICES = [29, 49, 79, 99, 129, 149, 199, 249]


@dataclass
class Recommendation:
    price: float
    respondents: int
    vw: VanWestendorp
    segments: pd.DataFrame
    take_rates: pd.DataFrame
    demand: DemandCurve
    sweep: pd.DataFrame
    assumptions: Assumptions
    pnl: pd.DataFrame
    summary: dict
    unit: dict
    risk: pd.DataFrame
    drivers: pd.DataFrame
    discount_tiers: pd.DataFrame


def choose_price(sweep: pd.DataFrame, vw: VanWestendorp, assumptions: Assumptions,
                 demand: DemandCurve) -> float:
    """Best-NPV charm price inside the Van Westendorp acceptable range.

    Customers read Rs 99 as much cheaper than Rs 104, so the final price is
    snapped to a familiar price point. Prices outside the range customers find
    acceptable are excluded even if the model likes them: they would draw
    complaints and support load the model does not capture.
    """
    candidates = [p for p in CHARM_PRICES if vw.pmc <= p <= vw.pme] or CHARM_PRICES
    values = {p: npv(replace(assumptions, price=float(p)), demand) for p in candidates}
    return float(max(values, key=values.get))


def discount_tiers(survey: pd.DataFrame, segments: pd.DataFrame, main_price: float,
                   assumptions: Assumptions) -> pd.DataFrame:
    """Suggest a cheaper tier for segments whose optimal price is far below the main price."""
    rows = []
    for row in segments.itertuples():
        if row.OPP >= 0.7 * main_price:
            continue
        tier_price = float(min(CHARM_PRICES, key=lambda p: abs(p - row.OPP)))
        orders = survey.loc[survey["segment"] == row.segment, "orders_per_month"].mean()
        unit = unit_economics(replace(assumptions, price=tier_price, baseline_orders=float(orders)))
        rows.append({"segment": row.segment, "segment_opp": row.OPP, "tier_price": tier_price,
                     "avg_orders_per_month": round(float(orders), 1),
                     "contribution_per_member": round(unit["contribution_per_member"], 1),
                     "viable": unit["contribution_per_member"] > 0})
    return pd.DataFrame(rows)


def recommend(survey: pd.DataFrame, assumptions: Assumptions | None = None, risk_runs: int = 5000,
              price: float | None = None) -> Recommendation:
    """Full analysis. Pass ``price`` to evaluate a specific price instead of the recommended one."""
    assumptions = assumptions or Assumptions()
    survey = validate_survey(survey)
    vw = van_westendorp(survey)
    segments = van_westendorp_by_segment(survey) if "segment" in survey.columns else pd.DataFrame()
    take_rates = stated_take_rates(survey)
    demand = fit_demand(take_rates)
    sweep = price_sweep(assumptions, demand)
    chosen = price if price is not None else choose_price(sweep, vw, assumptions, demand)
    final = replace(assumptions, price=float(chosen))
    pnl = project(final, demand)
    tiers = discount_tiers(survey, segments, chosen, final) if not segments.empty else pd.DataFrame()
    return Recommendation(chosen, len(survey), vw, segments, take_rates, demand, sweep, final, pnl,
                          summarise(pnl, final), unit_economics(final), monte_carlo(final, demand, runs=risk_runs),
                          tornado(final, demand), tiers)


def _crore(value: float) -> str:
    return f"Rs {value / CRORE:,.1f} crore"


def build_memo(rec: Recommendation) -> str:
    s, u, a, vw = rec.summary, rec.unit, rec.assumptions, rec.vw
    npvs = rec.risk["npv"]
    p10, p50, p90 = np.percentile(npvs, [10, 50, 90])
    best_sweep = rec.sweep.loc[rec.sweep["npv"].idxmax()]
    top_driver = rec.drivers.iloc[0]

    lines = [
        "# Pricing recommendation: FreshKart Plus", "",
        f"## Recommendation: launch at **Rs {rec.price:.0f} / month**", "",
        f"- Inside the range customers call acceptable (Rs {vw.pmc:.0f} to Rs {vw.pme:.0f}) and close to the "
        f"price they see as neither cheap nor expensive (Rs {vw.ipp:.0f}).",
        f"- 3-year NPV **{_crore(s['npv'])}**; payback in month **{s['payback_month']}**; "
        f"~{round(s['steady_state_members'], -3):,.0f} members at steady state.",
        f"- Each member contributes **Rs {u['contribution_per_member']:.0f}/month**: LTV:CAC of "
        f"{u['ltv_to_cac']:.1f}x, and CAC is paid back in {u['cac_payback_months']:.1f} months.",
        f"- Risk: NPV is positive in **{(npvs > 0).mean():.0%}** of {len(npvs):,} simulations "
        f"(P10 {_crore(p10)}, P50 {_crore(p50)}, P90 {_crore(p90)}).",
    ]
    if not rec.discount_tiers.empty:
        for tier in rec.discount_tiers.itertuples():
            verdict = "viable" if tier.viable else "NOT viable at current fees"
            lines.append(f"- Add a **{tier.segment} tier at Rs {tier.tier_price:.0f}** (their optimal price is "
                         f"Rs {tier.segment_opp:.0f}; contribution Rs {tier.contribution_per_member:.0f}/member/month, "
                         f"{verdict}). Gate it with ID verification so other users can't trade down.")

    lines += ["", f"## What customers told us (Van Westendorp, n = {rec.respondents:,})",
              "", "| Point | Price | Meaning |", "|---|---:|---|",
              f"| Marginal cheapness (PMC) | Rs {vw.pmc:.0f} | Below this, too many doubt the quality |",
              f"| Optimal (OPP) | Rs {vw.opp:.0f} | Fewest reject it as too cheap or too expensive |",
              f"| Indifference (IPP) | Rs {vw.ipp:.0f} | As many call it cheap as expensive |",
              f"| Marginal expensiveness (PME) | Rs {vw.pme:.0f} | Above this, too many reject it as too expensive |"]
    if not rec.segments.empty:
        lines += ["", "| Segment | Respondents | Acceptable range | Optimal |", "|---|---:|---|---:|"]
        for row in rec.segments.itertuples():
            lines.append(f"| {row.segment} | {row.respondents} | Rs {row.PMC:.0f} to {row.PME:.0f} | Rs {row.OPP:.0f} |")

    lines += ["", "## Demand (Gabor-Granger, calibrated for the say-do gap)", "",
              "| Price | Said 'definitely' | Calibrated take rate |", "|---:|---:|---:|"]
    for row in rec.take_rates.itertuples():
        lines.append(f"| Rs {row.price} | {row.definitely:.0%} | {row.take_rate:.1%} |")
    lines += ["", f"Demand is elastic around the recommended price (elasticity "
                  f"{rec.demand.elasticity(rec.price):.2f}): a 10% price rise loses about "
                  f"{abs(rec.demand.elasticity(rec.price)) * 10:.0f}% of sign-ups. The unrounded NPV-maximising price "
                  f"is Rs {best_sweep['price']:.0f}; the NPV curve is flat near the top, so rounding to Rs {rec.price:.0f} "
                  "costs little."]

    lines += ["", "## Unit economics (per member per month)", "", "| Line | Rs |", "|---|---:|",
              f"| Subscription fee | {u['subscription']:.0f} |",
              f"| Margin on {a.incremental_orders:g} extra orders | {u['extra_order_margin']:.0f} |",
              f"| Fees waived on {a.baseline_orders + a.incremental_orders:g} orders | {u['fees_waived']:.0f} |",
              f"| **Contribution** | **{u['contribution_per_member']:.0f}** |",
              "", f"Fee waivers are the hidden cost: they cancel out most of the subscription fee. Below about "
                  f"Rs {-(u['extra_order_margin'] + u['fees_waived']):.0f}/month, every member loses money."]

    lines += ["", "## What could go wrong", "",
              f"The biggest swing factor is **{top_driver['input'].replace('_', ' ')}**: moving it from "
              f"{top_driver['low_value']:g} to {top_driver['high_value']:g} moves NPV from "
              f"{_crore(top_driver['npv_at_low'])} to {_crore(top_driver['npv_at_high'])}.", "",
              "| Input | Low → High | NPV at low | NPV at high |", "|---|---|---:|---:|"]
    for row in rec.drivers.itertuples():
        lines.append(f"| {row.input.replace('_', ' ')} | {row.low_value:g} → {row.high_value:g} | "
                     f"{_crore(row.npv_at_low)} | {_crore(row.npv_at_high)} |")

    lines += ["", "## How to de-risk before full launch", "",
              "1. **Validate the take rate** with a fake-door test: show the Plus offer to 5% of eligible users and "
              "measure click-to-join, so we see what people do and not only what they say.",
              f"2. **Cap the fee waiver**: keep free delivery for baskets above Rs 99 only. Fees waived per "
              f"order is {'the biggest' if top_driver['input'] == 'fees_waived_per_order' else 'a major'} driver "
              "of NPV.",
              "3. **Measure incremental orders** with a 4-week member holdout. Extra orders are the main way "
              "Plus earns back the waived fees.",
              "4. **Price test by city cluster** (not by user) if needed, so neighbours never see different prices "
              "for the same product.",
              "5. **Kill criteria:** after 3 months, pause if contribution per member < Rs 20 or churn > 10%/month.",
              "", "_All data is synthetic, generated for this case study. FreshKart is fictional._", ""]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Recommend a membership price and build the business case.")
    parser.add_argument("--survey", type=Path, default=SAMPLE_SURVEY)
    parser.add_argument("--price", type=float, help="evaluate this price instead of the recommended one")
    parser.add_argument("--out", type=Path, default=Path("outputs/pricing_recommendation.md"))
    args = parser.parse_args()

    rec = recommend(pd.read_csv(args.survey), price=args.price)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(build_memo(rec), encoding="utf-8")
    rec.pnl.round(0).to_csv(args.out.parent / "pnl_36_months.csv", index=False)
    print(f"Price: Rs {rec.price:.0f}/month | NPV {_crore(rec.summary['npv'])} | "
          f"payback month {rec.summary['payback_month']} | P(NPV>0) {(rec.risk['npv'] > 0).mean():.0%}")
    print(f"Memo written to {args.out}")


if __name__ == "__main__":
    main()
