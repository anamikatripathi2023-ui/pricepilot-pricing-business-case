"""PricePilot dashboard. Run with:  streamlit run app.py"""
from __future__ import annotations

import io

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from pricepilot.business_case import CRORE, LAKH, Assumptions
from pricepilot.recommend import SAMPLE_SURVEY, build_memo, recommend

st.set_page_config(page_title="PricePilot - Pricing & Business Case", layout="wide")


@st.cache_data(show_spinner="Running pricing analysis and 5,000 risk simulations...")
def analyse(file_bytes: bytes | None, assumptions: Assumptions, price: float | None):
    survey = pd.read_csv(io.BytesIO(file_bytes) if file_bytes else SAMPLE_SURVEY)
    return recommend(survey, assumptions, price=price)


def crore(value: float) -> str:
    return f"Rs {value / CRORE:,.1f} cr"


# ---------------------------------------------------------------- sidebar
st.sidebar.title("PricePilot")
st.sidebar.caption("From a pricing survey to a price, a business case and a risk view.")
upload = st.sidebar.file_uploader("Upload survey CSV", type="csv",
                                  help="Same columns as data/pricing_survey.csv (Van Westendorp + Gabor-Granger).")
file_bytes = upload.getvalue() if upload else None

with st.sidebar.expander("Business assumptions", expanded=False):
    defaults = Assumptions()
    eligible = st.number_input("Eligible users (2+ orders/month)", 10_000, 50_000_000, defaults.eligible_users, 50_000)
    baseline_orders = st.slider("Orders/month a joiner already places", 1.0, 10.0, defaults.baseline_orders, 0.5)
    incremental = st.slider("Extra orders/month once a member", 0.0, 3.0, defaults.incremental_orders, 0.1)
    margin = st.slider("Contribution per order (Rs)", 10.0, 120.0, defaults.contribution_per_order, 5.0)
    fees = st.slider("Fees waived per order (Rs)", 0.0, 50.0, defaults.fees_waived_per_order, 1.0)
    churn = st.slider("Monthly churn", 0.01, 0.20, defaults.monthly_churn, 0.01)
    cac = st.slider("CAC per member (Rs)", 0.0, 500.0, defaults.cac, 10.0)
    build = st.number_input("Build cost (Rs lakh)", 0.0, 10_000.0, defaults.build_cost / LAKH, 10.0)
assumptions = Assumptions(eligible_users=int(eligible), baseline_orders=baseline_orders,
                          incremental_orders=incremental, contribution_per_order=margin,
                          fees_waived_per_order=fees, monthly_churn=churn, cac=cac, build_cost=build * LAKH)

override = st.sidebar.checkbox("Try my own price")
price = float(st.sidebar.slider("Price (Rs/month)", 29, 249, 99, 5)) if override else None

try:
    rec = analyse(file_bytes, assumptions, price)
except (ValueError, RuntimeError) as error:
    st.error(f"Could not analyse this survey: {error}")
    st.stop()

s, u, vw = rec.summary, rec.unit, rec.vw
st.title("FreshKart Plus: what should we charge?")
st.caption("FreshKart Plus (fictional): free delivery and no handling fee on orders above Rs 99, for a monthly fee.")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Price / month" if price is None else "Price tested", f"Rs {rec.price:.0f}",
          help="Recommended price" if price is None else "Your price")
c2.metric("3-yr NPV", crore(s["npv"]))
c3.metric("Payback", f"{s['payback_month']} mo" if s["payback_month"] is not None else "never",
          help="Month in which cumulative cash turns positive")
c4.metric("Members", f"{s['steady_state_members'] / 1000:,.0f}k", help="Members at steady state")
c5.metric("P(NPV > 0)", f"{(rec.risk['npv'] > 0).mean():.0%}")

tab_wtp, tab_demand, tab_case, tab_risk, tab_memo = st.tabs(
    ["1. Willingness to pay", "2. Demand & price", "3. Business case", "4. Risk", "5. Recommendation"])

# ---------------------------------------------------------------- WTP
with tab_wtp:
    curves = rec.vw.curves.melt(id_vars="price", value_vars=["too cheap", "not cheap", "not expensive",
                                                             "too expensive"], var_name="answer", value_name="share")
    fig = px.line(curves, x="price", y="share", color="answer",
                  title="Van Westendorp: where the curves cross sets the acceptable range")
    fig.add_vrect(x0=vw.pmc, x1=vw.pme, fillcolor="green", opacity=0.08, line_width=0,
                  annotation_text="acceptable range", annotation_position="bottom left")
    points = [("PMC", vw.pmc), ("OPP", vw.opp), ("IPP", vw.ipp), ("PME", vw.pme)]
    for i, (name, value) in enumerate(points):
        fig.add_vline(x=value, line_dash="dot", line_color="grey")
        fig.add_annotation(x=value, y=1.0 - 0.09 * i, text=f"{name} Rs {value:.0f}", showarrow=False,
                           xanchor="left", bgcolor="rgba(255,255,255,0.7)")
    fig.update_layout(xaxis_range=[0, vw.pme * 1.6], yaxis_tickformat=".0%")
    st.plotly_chart(fig, width="stretch")
    if not rec.segments.empty:
        st.write("**By segment:** students would pay much less, which points to a separate student tier.")
        st.dataframe(rec.segments, hide_index=True, width="stretch")
    if not rec.discount_tiers.empty:
        st.dataframe(rec.discount_tiers, hide_index=True, width="stretch")

# ---------------------------------------------------------------- demand
with tab_demand:
    grid = np.arange(29, 250, 1)
    smooth = pd.DataFrame({"price": grid, "take_rate": rec.demand.take_rate(grid)})
    fig = px.line(smooth, x="price", y="take_rate", title="Calibrated take rate: survey points and fitted demand curve")
    fig.add_scatter(x=rec.take_rates["price"], y=rec.take_rates["take_rate"], mode="markers", name="survey",
                    marker={"size": 10})
    fig.update_layout(yaxis_tickformat=".0%")
    st.plotly_chart(fig, width="stretch")
    sweep = rec.sweep.assign(npv_crore=rec.sweep["npv"] / CRORE)
    fig = px.line(sweep, x="price", y="npv_crore", title="3-year NPV by price (Rs crore)", markers=True)
    fig.add_vline(x=rec.price, line_dash="dash", annotation_text=f"Rs {rec.price:.0f}")
    fig.add_hline(y=0, line_color="grey")
    st.plotly_chart(fig, width="stretch")
    st.caption(f"Price elasticity at Rs {rec.price:.0f}: {rec.demand.elasticity(rec.price):.2f}. Too cheap loses "
               "money on every member (fee waivers); too expensive and too few people join.")

# ---------------------------------------------------------------- business case
with tab_case:
    waterfall = go.Figure(go.Waterfall(
        x=["Subscription", "Extra-order margin", "Fees waived", "Contribution"],
        y=[u["subscription"], u["extra_order_margin"], u["fees_waived"], 0],
        measure=["relative", "relative", "relative", "total"]))
    waterfall.update_layout(title="Unit economics: monthly contribution per member (Rs)")
    st.plotly_chart(waterfall, width="stretch")
    c1, c2, c3 = st.columns(3)
    c1.metric("Contribution / member / month", f"Rs {u['contribution_per_member']:.0f}")
    c2.metric("LTV : CAC", f"{u['ltv_to_cac']:.1f}x")
    c3.metric("CAC payback", f"{u['cac_payback_months']:.1f} months")

    pnl = rec.pnl
    fig = go.Figure()
    fig.add_bar(x=pnl["month"], y=pnl["net"] / LAKH, name="monthly net (Rs lakh)")
    fig.add_scatter(x=pnl["month"], y=pnl["cumulative"] / LAKH, name="cumulative (Rs lakh)", mode="lines")
    fig.update_layout(title="36-month cash view", xaxis_title="month")
    st.plotly_chart(fig, width="stretch")
    st.download_button("Download 36-month P&L (CSV)", pnl.round(0).to_csv(index=False), "pnl_36_months.csv")

# ---------------------------------------------------------------- risk
with tab_risk:
    npv = rec.risk["npv"] / CRORE
    fig = px.histogram(npv, nbins=50, title=f"NPV across {len(npv):,} simulated futures (Rs crore)")
    fig.add_vline(x=0, line_color="red")
    fig.update_layout(showlegend=False, xaxis_title="3-year NPV (Rs crore)")
    st.plotly_chart(fig, width="stretch")
    p10, p50, p90 = np.percentile(npv, [10, 50, 90])
    st.write(f"P10 **Rs {p10:.1f} cr** · P50 **Rs {p50:.1f} cr** · P90 **Rs {p90:.1f} cr**")

    drivers = rec.drivers.iloc[::-1]
    base = drivers["base_npv"].iloc[0] / CRORE
    fig = go.Figure()
    fig.add_bar(y=drivers["input"], x=drivers["npv_at_low"] / CRORE - base, base=base, orientation="h",
                name="input at low")
    fig.add_bar(y=drivers["input"], x=drivers["npv_at_high"] / CRORE - base, base=base, orientation="h",
                name="input at high")
    fig.update_layout(barmode="overlay", title="Tornado: what moves NPV most (Rs crore)")
    st.plotly_chart(fig, width="stretch")

# ---------------------------------------------------------------- memo
with tab_memo:
    memo = build_memo(rec)
    st.download_button("Download recommendation (Markdown)", memo, "pricing_recommendation.md")
    st.markdown(memo)
