# Pricing recommendation: FreshKart Plus

## Recommendation: launch at **Rs 99 / month**

- Inside the range customers call acceptable (Rs 50 to Rs 144) and close to the price they see as neither cheap nor expensive (Rs 94).
- 3-year NPV **Rs 16.7 crore**; payback in month **11**; ~182,000 members at steady state.
- Each member contributes **Rs 59/month**: LTV:CAC of 6.6x, and CAC is paid back in 2.5 months.
- Risk: NPV is positive in **96%** of 5,000 simulations (P10 Rs 2.9 crore, P50 Rs 12.3 crore, P90 Rs 22.5 crore).
- Add a **student tier at Rs 49** (their optimal price is Rs 50; contribution Rs 24/member/month, viable). Gate it with ID verification so other users can't trade down.

## What customers told us (Van Westendorp, n = 1,200)

| Point | Price | Meaning |
|---|---:|---|
| Marginal cheapness (PMC) | Rs 50 | Below this, too many doubt the quality |
| Optimal (OPP) | Rs 75 | Fewest reject it as too cheap or too expensive |
| Indifference (IPP) | Rs 94 | As many call it cheap as expensive |
| Marginal expensiveness (PME) | Rs 144 | Above this, too many reject it as too expensive |

| Segment | Respondents | Acceptable range | Optimal |
|---|---:|---|---:|
| family | 309 | Rs 66 to 194 | Rs 110 |
| student | 348 | Rs 31 to 89 | Rs 50 |
| young professional | 543 | Rs 56 to 159 | Rs 81 |

## Demand (Gabor-Granger, calibrated for the say-do gap)

| Price | Said 'definitely' | Calibrated take rate |
|---:|---:|---:|
| Rs 49 | 76% | 56.5% |
| Rs 79 | 45% | 36.2% |
| Rs 99 | 29% | 25.0% |
| Rs 129 | 15% | 13.6% |
| Rs 149 | 9% | 8.4% |
| Rs 199 | 3% | 3.2% |

Demand is elastic around the recommended price (elasticity -1.96): a 10% price rise loses about 20% of sign-ups. The unrounded NPV-maximising price is Rs 104; the NPV curve is flat near the top, so rounding to Rs 99 costs little.

## Unit economics (per member per month)

| Line | Rs |
|---|---:|
| Subscription fee | 99 |
| Margin on 1.2 extra orders | 54 |
| Fees waived on 5.2 orders | -94 |
| **Contribution** | **59** |

Fee waivers are the hidden cost: they cancel out most of the subscription fee. Below about Rs 40/month, every member loses money.

## What could go wrong

The biggest swing factor is **fees waived per order**: moving it from 12 to 26 moves NPV from Rs 30.9 crore to Rs -2.3 crore.

| Input | Low → High | NPV at low | NPV at high |
|---|---|---:|---:|
| fees waived per order | 12 → 26 | Rs 30.9 crore | Rs -2.3 crore |
| incremental orders | 0.5 → 1.8 | Rs 8.0 crore | Rs 24.1 crore |
| intent calibration | 0.6 → 1.2 | Rs 8.4 crore | Rs 20.8 crore |
| cac | 80 → 250 | Rs 19.7 crore | Rs 12.3 crore |
| monthly churn | 0.04 → 0.1 | Rs 18.0 crore | Rs 14.0 crore |

## How to de-risk before full launch

1. **Validate the take rate** with a fake-door test: show the Plus offer to 5% of eligible users and measure click-to-join, so we see what people do and not only what they say.
2. **Cap the fee waiver**: keep free delivery for baskets above Rs 99 only. Fees waived per order is the biggest driver of NPV.
3. **Measure incremental orders** with a 4-week member holdout. Extra orders are the main way Plus earns back the waived fees.
4. **Price test by city cluster** (not by user) if needed, so neighbours never see different prices for the same product.
5. **Kill criteria:** after 3 months, pause if contribution per member < Rs 20 or churn > 10%/month.

_All data is synthetic, generated for this case study. FreshKart is fictional._
