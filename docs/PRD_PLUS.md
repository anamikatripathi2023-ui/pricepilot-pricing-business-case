# PRD: FreshKart Plus membership

| | |
|---|---|
| **Status** | Pricing analysis complete; ready for fake-door test |
| **Area** | Monetisation & retention |
| **Product** | FreshKart (fictional 10-minute grocery app, ~2M monthly active users, India) |

## 1. Problem

**For customers:** frequent shoppers pay a delivery fee plus a handling fee on most orders. Fee complaints rose sharply after the handling fee was introduced. Small top-up orders ("just milk and bread") feel overpriced, so customers batch orders or go to the local store.

**For the business:** order frequency drives contribution margin, but fees discourage exactly the small, frequent orders a 10-minute app exists for.

**Opportunity:** swap per-order fees for a predictable monthly fee. Customers get a simpler deal; FreshKart gets more orders and better retention.

## 2. Target users

| Segment | Share of survey | Orders/month | What they value |
|---|---:|---:|---|
| Young professionals | 45% | ~5 | Convenience, no fee anxiety for small orders |
| Families | 25% | ~6 | Savings on frequent large baskets |
| Students | 30% | ~3 | Low price; very price-sensitive |

## 3. Value proposition

> "Order as often as you like. No delivery fee, no handling fee, on every order above ₹99, for one monthly price."

## 4. Requirements

| Priority | Requirement |
|---|---|
| P0 | Monthly subscription with UPI Autopay; cancel anytime in two taps |
| P0 | Fees waived automatically at checkout, shown as "You saved ₹X with Plus" |
| P0 | Minimum basket (₹99) for free delivery, to cap the cost of fee waivers |
| P1 | Monthly savings summary ("Plus saved you ₹240 this month"), to fight churn |
| P1 | Student tier with ID verification |
| P2 | Member-only deals; family sharing |

**Non-goals (v1):** annual plans (until monthly churn is known); bundling with partner services.

## 5. Success metrics

| Type | Metric | Target (3 months after launch) |
|---|---|---|
| North star | Orders per member per month | +1.2 vs matched non-members |
| Business | Contribution per member per month | ≥ ₹40 (kill if < ₹20) |
| Adoption | Members ÷ eligible users | ≥ 15% |
| Retention | Monthly churn | ≤ 6% (kill if > 10%) |
| Guardrail | Non-member conversion | No drop (Plus must not make non-members feel penalised) |
| Guardrail | Fee-related complaints | Down ≥ 30% |

## 6. Risks

| Risk | Mitigation |
|---|---|
| Heavy users join first and cost more in waived fees | ₹99 minimum basket; monitor fees waived per member weekly |
| Stated purchase intent overstates real demand | Calibrated take rates + fake-door test before build |
| Members order the same amount, so there is no incremental margin | 4-week holdout to measure true lift |
| Trade-down to the student tier | ID verification; student tier limited to a set of app features |
| Regulatory: auto-renewal and price-change rules | Clear renewal reminders; price changes need opt-in consent; Legal review before launch |

## 7. Pricing

See the [generated recommendation](../outputs/pricing_recommendation.md): **₹99/month**, plus a **₹49 student tier**.
