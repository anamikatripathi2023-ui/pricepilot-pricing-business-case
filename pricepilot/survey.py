"""Synthetic pricing survey for "FreshKart Plus", a monthly delivery membership.

FreshKart Plus (fictional): free delivery and no handling fee on every order
above Rs 99, plus member-only deals. The survey asks 1,200 current customers
two standard pricing question sets:

* **Van Westendorp Price Sensitivity Meter**: at what monthly price would
  Plus be so cheap you'd doubt the quality / a bargain / getting expensive /
  too expensive to consider?
* **Gabor-Granger**: how likely would you be to buy at Rs 49, 79, 99, 129, 149, 199?

Answers are generated from a hidden willingness-to-pay (WTP) per respondent
that depends on their segment, city tier and how often they order, plus the
noise and inconsistency real respondents show.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

PRICE_POINTS = [49, 79, 99, 129, 149, 199]
INTENT_SCALE = ["definitely not", "probably not", "maybe", "probably", "definitely"]

SEGMENTS = {
    # name: (share of respondents, median WTP in Rs/month, mean orders per month)
    "student": (0.30, 70, 3.0),
    "young professional": (0.45, 125, 5.0),
    "family": (0.25, 150, 6.0),
}


def _round5(values: np.ndarray) -> np.ndarray:
    return (np.round(values / 5) * 5).clip(min=5)


def generate_survey(n: int = 1200, seed: int = 21) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    names = list(SEGMENTS)
    shares = np.array([SEGMENTS[s][0] for s in names])
    segment = rng.choice(names, size=n, p=shares / shares.sum())
    tier2 = rng.random(n) < 0.3
    mean_orders = np.array([SEGMENTS[s][2] for s in segment])
    orders = np.maximum(1, rng.poisson(mean_orders))

    median_wtp = np.array([SEGMENTS[s][1] for s in segment]) * np.where(tier2, 0.8, 1.0)
    order_effect = (orders / mean_orders) ** 0.35           # heavier users value free delivery more
    wtp = median_wtp * order_effect * rng.lognormal(0, 0.35, n)

    too_cheap = _round5(wtp * rng.uniform(0.25, 0.45, n))
    cheap = np.maximum(_round5(wtp * rng.uniform(0.55, 0.85, n)), too_cheap + 5)
    expensive = np.maximum(_round5(wtp * rng.uniform(1.05, 1.35, n)), cheap + 5)
    too_expensive = np.maximum(_round5(wtp * rng.uniform(1.45, 1.95, n)), expensive + 5)

    df = pd.DataFrame({
        "respondent_id": [f"S{i:04d}" for i in range(1, n + 1)],
        "segment": segment,
        "city_tier": np.where(tier2, "Tier 2", "Tier 1"),
        "orders_per_month": orders,
        "vw_too_cheap": too_cheap.astype(int),
        "vw_cheap": cheap.astype(int),
        "vw_expensive": expensive.astype(int),
        "vw_too_expensive": too_expensive.astype(int),
    })
    # Stated intent: a latent score centred on (WTP - price), bucketed into 5 answers.
    for price in PRICE_POINTS:
        score = (wtp - price) / (0.25 * wtp) + rng.normal(0, 0.6, n)
        bucket = np.digitize(score, [-1.5, -0.5, 0.3, 1.0])
        df[f"gg_{price}"] = np.array(INTENT_SCALE)[bucket]
    return df


def main() -> None:
    from pathlib import Path

    out = Path(__file__).resolve().parent.parent / "data" / "pricing_survey.csv"
    df = generate_survey()
    df.to_csv(out, index=False)
    print(f"Wrote {len(df):,} survey responses to {out}")


if __name__ == "__main__":
    main()
