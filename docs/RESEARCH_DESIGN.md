# Research design: pricing survey

## Objective

Estimate how much FreshKart customers would pay for Plus, how demand changes with price, and how this differs by segment, before committing engineering effort.

## Sample

| | |
|---|---|
| Who | Customers with ≥ 2 orders in the last 30 days (the eligible base) |
| Size | 1,200 completes, which gives ±2.8 pp margin of error on a take rate at 95% confidence |
| Quotas | Segment and city tier set to match the eligible base, so results are not skewed toward whoever answers surveys |
| Incentive | ₹25 wallet credit, the same for everyone (a bigger incentive would attract bargain hunters) |

## Questionnaire

**Part A: context**
1. How many orders did you place on FreshKart in the last month? *(checked against order history)*
2. Which best describes you? Student / working professional / family household / other

**Part B: concept** *(the same short description for everyone)*
> *FreshKart Plus: no delivery fee and no handling fee on every order above ₹99, plus member-only deals. Billed monthly, cancel anytime.*

**Part C: Van Westendorp** *(open numeric answers, ₹ per month)*
3. At what price would Plus be **so cheap** that you'd doubt it's any good?
4. At what price would it be a **bargain**, a great deal?
5. At what price would it start to feel **expensive**, though you'd still consider it?
6. At what price would it be **too expensive** to consider?

**Part D: Gabor-Granger** *(randomised price order, one price per screen)*
7. If Plus cost ₹X per month, how likely would you be to join? Definitely not / Probably not / Maybe / Probably / Definitely
   X ∈ {49, 79, 99, 129, 149, 199}

## Bias controls

| Bias | Control |
|---|---|
| Anchoring on the first price shown | Gabor-Granger prices in random order; Van Westendorp asked first, with no price shown |
| Inconsistent answers | Respondents whose four Van Westendorp answers are out of order are dropped (`validate_survey`) |
| Say-do gap (people overstate intent) | Count 70% of "definitely" + 30% of "probably" as buyers; then stress-test that calibration from 0.6x to 1.2x in the risk model |
| Non-response | Quotas, plus a comparison of respondents with non-respondents on order history |

## Why two methods?

| | Van Westendorp | Gabor-Granger |
|---|---|---|
| Answers | "What price range feels acceptable?" | "How many would buy at each price?" |
| Strength | No price anchoring; shows perception | Gives a demand curve, which revenue modelling needs |
| Weakness | No volume estimate | Anchors on the prices shown |

Using both lets each cover the other's blind spot: Van Westendorp sets the **range**, Gabor-Granger plus the business case picks the **point** inside it.

## What would change the recommendation

- Fake-door click-to-join below 60% of the calibrated take rate → re-run at a lower price point.
- Student answers with a much higher variance than the other segments → too few students; extend the sample.
