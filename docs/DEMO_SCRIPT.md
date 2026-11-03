# 5-minute demo script

**Setup:** `streamlit run app.py`.

| Time | Screen | What to say |
|---|---|---|
| 0:00 | Header metrics | "FreshKart customers were complaining about fees. The idea: a membership that removes them. The question every PM dreads: what do we charge? PricePilot's answer is ₹99, with a 96% chance of positive NPV. Let me show how it gets there." |
| 0:30 | **1. Willingness to pay** | "1,200 customers answered four price questions. Where the curves cross gives the acceptable range: ₹50 to ₹144. By segment, students would pay half what families would. That's the first hint we need two tiers." |
| 1:15 | **2. Demand & price** | "Stated intent is inflated, so I calibrate it. Then I fit a demand curve. Look at the NPV curve: at low prices NPV is deeply negative. Every member costs us waived fees, so more cheap members means a bigger loss. The optimum is ₹104; it's flat at the top, so ₹99 costs nothing and reads better." |
| 2:15 | **3. Business case** | "The waterfall is the whole story: ₹99 fee plus ₹54 from extra orders, minus ₹94 of waived fees, leaves ₹59 per member per month. LTV to CAC is 6.6x; payback is month 11." |
| 3:00 | **4. Risk** | "These are 5,000 possible futures. 96% are profitable. The tornado shows the biggest risk isn't demand, it's fees waived per order. At ₹26 per order, the case goes negative. So the ₹99 minimum basket for free delivery is a P0 requirement, not a detail." *(Open the assumptions and drag the fees slider to 26 to show it live.)* |
| 4:00 | **5. Recommendation** | "The memo says: ₹99, a verified student tier at ₹49, and de-risk with a fake-door test, a holdout to measure extra orders, and city-level price tests. Kill criteria are written in advance." |
| 4:40 | Close | "The point isn't the number ₹99. It's that every assumption behind it is visible, testable and has a plan to be tested." |

## Likely questions

- **Why trust a survey?** I don't fully: it's calibrated, stress-tested, and validated with a fake door before build. See the [research design](RESEARCH_DESIGN.md).
- **Why not test prices by user?** Fairness; see [D7](DECISIONS.md).
- **What if a competitor launches at ₹49?** Re-run with a lower calibration and a higher churn; the tornado shows how much room there is. A competitor scenario is the next feature.
- **How would you measure success after launch?** Orders per member vs a matched holdout, plus contribution per member. See the [PRD](PRD_PLUS.md#5-success-metrics).
