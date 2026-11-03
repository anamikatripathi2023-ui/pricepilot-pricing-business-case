from dataclasses import replace

import numpy as np
import pandas as pd
import pytest

from pricepilot.business_case import Assumptions, npv, project, summarise, tornado, unit_economics
from pricepilot.pricing import (_crossing, fit_demand, stated_take_rates, validate_survey, van_westendorp,
                                van_westendorp_by_segment)
from pricepilot.recommend import SAMPLE_SURVEY, build_memo, recommend
from pricepilot.survey import PRICE_POINTS, generate_survey


@pytest.fixture(scope="module")
def survey():
    return validate_survey(pd.read_csv(SAMPLE_SURVEY))


@pytest.fixture(scope="module")
def rec(survey):
    return recommend(survey, risk_runs=300)


# ---------------------------------------------------------------- survey & WTP
def test_generator_is_reproducible():
    pd.testing.assert_frame_equal(generate_survey(200, seed=1), generate_survey(200, seed=1))


def test_validation_drops_inconsistent_answers(survey):
    bad = survey.head(40).copy()
    bad.loc[0, "vw_cheap"] = bad.loc[0, "vw_too_expensive"] + 10      # out of order
    assert len(validate_survey(bad)) == 39
    with pytest.raises(ValueError, match="missing"):
        validate_survey(bad.drop(columns=["gg_99"]))


def test_crossing_interpolates():
    prices = np.array([0, 10, 20])
    assert _crossing(prices, np.array([1.0, 0.6, 0.2]), np.array([0.0, 0.4, 0.8])) == pytest.approx(12.5)


def test_van_westendorp_points_are_ordered(survey):
    vw = van_westendorp(survey)
    assert vw.pmc < vw.opp < vw.pme
    assert vw.pmc < vw.ipp < vw.pme
    assert 40 < vw.opp < 120


def test_students_value_it_least(survey):
    by_segment = van_westendorp_by_segment(survey).set_index("segment")
    assert by_segment.loc["student", "OPP"] < by_segment.loc["young professional", "OPP"] \
        < by_segment.loc["family", "OPP"]


def test_take_rate_falls_with_price(survey):
    rates = stated_take_rates(survey)["take_rate"].values
    assert (np.diff(rates) < 0).all()
    demand = fit_demand(stated_take_rates(survey))
    assert np.abs(demand.take_rate(PRICE_POINTS) - rates).max() < 0.05
    assert demand.elasticity(99) < -1                                   # elastic


# ---------------------------------------------------------------- business case
def test_unit_economics_by_hand():
    unit = unit_economics(Assumptions(price=99, baseline_orders=4, incremental_orders=1.2,
                                      contribution_per_order=45, fees_waived_per_order=18, cac=150))
    assert unit["contribution_per_member"] == pytest.approx(99 + 54 - 93.6)
    assert unit["cac_payback_months"] == pytest.approx(150 / 59.4)


def test_pnl_adds_up(rec):
    pnl = rec.pnl
    parts = pnl[["subscription_revenue", "extra_order_margin", "fees_waived", "acquisition_cost", "fixed_cost"]]
    np.testing.assert_allclose(parts.sum(axis=1), pnl["net"])
    assert pnl.loc[0, "net"] == -rec.assumptions.build_cost
    assert pnl["members"].iloc[-1] > pnl["members"].iloc[6] > 0


def test_cheaper_is_not_always_better(rec):
    a = rec.assumptions
    npv = {p: summarise(project(replace(a, price=p), rec.demand), replace(a, price=p))["npv"] for p in (29, 99, 249)}
    assert npv[99] > npv[29] and npv[99] > npv[249]


def test_fee_waivers_can_sink_the_case(rec):
    a = replace(rec.assumptions, fees_waived_per_order=40)
    assert summarise(project(a, rec.demand), a)["npv"] < 0


def test_fast_npv_matches_full_pnl(rec):
    a = rec.assumptions
    assert npv(a, rec.demand) == pytest.approx(summarise(project(a, rec.demand), a)["npv"])


def test_tornado_is_sorted(rec):
    swings = tornado(rec.assumptions, rec.demand)["swing"].values
    assert (np.diff(swings) <= 0).all()


# ---------------------------------------------------------------- recommendation
def test_recommends_a_charm_price_in_range(rec):
    assert rec.price == 99
    assert rec.vw.pmc <= rec.price <= rec.vw.pme
    assert rec.summary["npv"] > 0 and rec.summary["payback_month"] is not None


def test_student_tier_suggested(rec):
    tiers = rec.discount_tiers.set_index("segment")
    assert tiers.loc["student", "tier_price"] == 49
    assert bool(tiers.loc["student", "viable"])


def test_memo_mentions_the_essentials(rec):
    memo = build_memo(rec)
    for text in ("Rs 99 / month", "NPV", "student tier", "fake-door"):
        assert text in memo


def test_price_override(survey):
    rec = recommend(survey, risk_runs=50, price=149)
    assert rec.price == 149
