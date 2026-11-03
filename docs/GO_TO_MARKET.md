# Go-to-market plan: FreshKart Plus

## Positioning

| | |
|---|---|
| **For** | FreshKart customers who order 2+ times a month |
| **Who** | are tired of paying fees on small, frequent orders |
| **Plus is** | a monthly membership |
| **That** | removes delivery and handling fees on every order above ₹99 |
| **Unlike** | paying fees each time, or batching orders to avoid them |
| **We** | show you exactly how much you saved every month |

**Message tested in the fake door:** *"Never pay a delivery fee again. ₹99/month."* vs *"Save ₹200+ a month on fees."* (loss-framing vs gain-framing).

## Launch phases

| Phase | What | Duration | Go / no-go |
|---|---|---|---|
| **0. Fake door** | "Join Plus" banner for 5% of eligible users → "Coming soon, join the waitlist" | 2 weeks | Click-to-waitlist ≥ 60% of the calibrated take rate |
| **1. Pilot** | Real membership at ₹99 in 2 city clusters; 4-week holdout to measure incremental orders | 6 weeks | Extra orders ≥ 0.8/member/month; contribution ≥ ₹40 |
| **2. Pricing test** | ₹79 vs ₹99 vs ₹129 by **city cluster** | 4 weeks | Pick the price with the best contribution per eligible user |
| **3. National launch** | All cities, plus the student tier | — | Kill criteria are reviewed monthly |

## Why test prices by city cluster, not by user

Showing two neighbours different prices for the same product feels unfair. When it is discovered, it damages trust far more than any revenue gained. Randomising by city cluster keeps prices consistent where people talk to each other. It needs more time (fewer units), which is why the test runs 4 weeks.

## Launch checklist

| Team | Deliverable |
|---|---|
| Engineering | Subscription billing with UPI Autopay, fee waiver at checkout, savings tracker |
| Design | Plus badge, "You saved ₹X" checkout line, two-tap cancellation |
| Marketing | Fake-door copy test, launch push notification, referral offer |
| Legal | Auto-renewal disclosure, price-change consent flow, student verification privacy review |
| Support | FAQ, macros for billing questions, refund policy |
| Finance | Revenue recognition for subscriptions; weekly contribution dashboard |

## Kill and scale criteria (monthly review)

| Signal | Action |
|---|---|
| Contribution per member < ₹20 for 2 months | Pause sign-ups; raise the minimum basket or the price |
| Churn > 10% / month | Interview churned members; test an annual plan |
| Contribution ≥ ₹60 and churn ≤ 5% | Scale marketing spend (raise the CAC ceiling to ₹250) |
