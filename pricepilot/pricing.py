"""Willingness-to-pay analysis: Van Westendorp and Gabor-Granger."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

from .survey import PRICE_POINTS

VW_COLUMNS = ["vw_too_cheap", "vw_cheap", "vw_expensive", "vw_too_expensive"]
REQUIRED_COLUMNS = set(VW_COLUMNS) | {f"gg_{p}" for p in PRICE_POINTS}


def validate_survey(survey: pd.DataFrame) -> pd.DataFrame:
    """Check columns and drop respondents whose four Van Westendorp answers are out of order."""
    missing = REQUIRED_COLUMNS - set(survey.columns)
    if missing:
        raise ValueError(f"Survey file is missing column(s): {', '.join(sorted(missing))}")
    answers = survey[VW_COLUMNS].apply(pd.to_numeric, errors="coerce")
    consistent = (answers.notna().all(axis=1)
                  & (answers["vw_too_cheap"] < answers["vw_cheap"])
                  & (answers["vw_cheap"] < answers["vw_expensive"])
                  & (answers["vw_expensive"] < answers["vw_too_expensive"]))
    cleaned = survey[consistent].copy()
    if len(cleaned) < 30:
        raise ValueError("Fewer than 30 consistent Van Westendorp responses; need more data.")
    cleaned[VW_COLUMNS] = answers[consistent]
    return cleaned.reset_index(drop=True)


# ---------------------------------------------------------------- Van Westendorp
@dataclass
class VanWestendorp:
    curves: pd.DataFrame
    pmc: float   # point of marginal cheapness: lower bound of the acceptable range
    opp: float   # optimal price point: fewest people reject it as too cheap or too expensive
    ipp: float   # indifference price point: as many call it cheap as expensive
    pme: float   # point of marginal expensiveness: upper bound of the acceptable range


def _crossing(prices: np.ndarray, falling: np.ndarray, rising: np.ndarray) -> float:
    """Price where a falling curve meets a rising one (linear interpolation)."""
    diff = falling - rising
    idx = np.where(np.diff(np.sign(diff)) != 0)[0]
    if len(idx) == 0:
        return float("nan")
    i = idx[0]
    if diff[i] == diff[i + 1]:
        return float(prices[i])
    return float(prices[i] + (prices[i + 1] - prices[i]) * diff[i] / (diff[i] - diff[i + 1]))


def van_westendorp(survey: pd.DataFrame, step: float = 1.0) -> VanWestendorp:
    top = survey["vw_too_expensive"].max() * 1.1
    prices = np.arange(0, top + step, step)
    share = lambda column, op: np.array([op(survey[column], p).mean() for p in prices])  # noqa: E731
    curves = pd.DataFrame({
        "price": prices,
        "too cheap": share("vw_too_cheap", lambda s, p: s >= p),
        "cheap": share("vw_cheap", lambda s, p: s >= p),
        "expensive": share("vw_expensive", lambda s, p: s <= p),
        "too expensive": share("vw_too_expensive", lambda s, p: s <= p),
    })
    curves["not cheap"] = 1 - curves["cheap"]
    curves["not expensive"] = 1 - curves["expensive"]
    return VanWestendorp(
        curves=curves,
        pmc=_crossing(prices, curves["too cheap"].values, curves["not cheap"].values),
        opp=_crossing(prices, curves["too cheap"].values, curves["too expensive"].values),
        ipp=_crossing(prices, curves["cheap"].values, curves["expensive"].values),
        pme=_crossing(prices, curves["not expensive"].values, curves["too expensive"].values),
    )


def van_westendorp_by_segment(survey: pd.DataFrame, column: str = "segment") -> pd.DataFrame:
    rows = []
    for value, group in survey.groupby(column):
        if len(group) < 30:
            continue
        vw = van_westendorp(group)
        rows.append({column: value, "respondents": len(group), "PMC": vw.pmc, "OPP": vw.opp,
                     "IPP": vw.ipp, "PME": vw.pme})
    return pd.DataFrame(rows).round(0)


# ---------------------------------------------------------------- Gabor-Granger
def stated_take_rates(survey: pd.DataFrame, definitely_weight: float = 0.7,
                      probably_weight: float = 0.3) -> pd.DataFrame:
    """Share who would buy at each price, calibrated for the say-do gap.

    People overstate purchase intent. A common rule of thumb counts 70% of
    "definitely" and 30% of "probably" answers as real buyers. The weights are
    an assumption, so they are exposed and stress-tested in the risk model.
    """
    rows = []
    for price in PRICE_POINTS:
        answers = survey[f"gg_{price}"].str.lower()
        definitely, probably = answers.eq("definitely").mean(), answers.eq("probably").mean()
        rows.append({"price": price, "definitely": definitely, "probably": probably,
                     "take_rate": definitely_weight * definitely + probably_weight * probably})
    return pd.DataFrame(rows)


def _logistic(price, ceiling, midpoint, scale):
    return ceiling / (1 + np.exp((price - midpoint) / scale))


@dataclass
class DemandCurve:
    ceiling: float
    midpoint: float
    scale: float

    def take_rate(self, price):
        return _logistic(np.asarray(price, float), self.ceiling, self.midpoint, self.scale)

    def elasticity(self, price: float) -> float:
        """% change in take rate for a 1% price increase (negative = demand falls)."""
        return float(-(price / self.scale) * (1 - self.take_rate(price) / self.ceiling))


def fit_demand(take_rates: pd.DataFrame) -> DemandCurve:
    """Fit a smooth logistic demand curve through the calibrated take rates."""
    x, y = take_rates["price"].values.astype(float), take_rates["take_rate"].values.astype(float)
    start = [max(y.max() * 1.2, 1e-3), float(np.median(x)), 30.0]
    (ceiling, midpoint, scale), _ = curve_fit(_logistic, x, y, p0=start,
                                              bounds=([0, 0, 1], [1, 1000, 500]), maxfev=20000)
    return DemandCurve(float(ceiling), float(midpoint), float(scale))
