# Decision log

## D1. Optimise NPV, not revenue or member count

- **Revenue-maximising** prices ignore that every member costs waived fees.
- **Member-maximising** prices (the lowest price) lose money below about ₹40/month.
- **NPV** captures fee, margin on extra orders, waived fees, churn, CAC, build cost and the time value of money in one number. It is the metric finance will hold the launch to.

## D2. Only consider prices inside the Van Westendorp acceptable range

The financial model does not know about brand damage, complaints or "this is a rip-off" reviews. If the model's optimum sits outside the range customers call acceptable, those costs are real but invisible. The acceptable range acts as a guardrail on the optimiser.

## D3. Charm pricing: ₹99, not ₹104

The NPV curve is flat near the top: ₹99 is within 1% of the ₹104 optimum, and anything from ₹94 to ₹114 is within 3%. ₹99 is a familiar price point that reads as "under ₹100". When the model is indifferent, customer perception decides.

## D4. Calibrate stated intent, then stress-test the calibration

Survey respondents overstate how likely they are to buy. Counting 70% of "definitely" and 30% of "probably" is a common rule of thumb, but it is an *assumption*. So it is one of the five inputs in the Monte Carlo (0.6x to 1.2x), and the fake-door test measures it directly before any build.

## D5. Monte Carlo over best/worst case

A best case and worst case have no probabilities attached, so leadership cannot tell how likely each is. Sampling five uncertain inputs 5,000 times gives a *distribution*: "NPV is positive in 96% of futures, with a P10 of ₹2.9 crore". The tornado chart then shows which input to de-risk first. Here it is fees waived per order, which led directly to the ₹99 minimum-basket requirement.

## D6. Student tier only with verification

Students' optimal price (₹50) is less than half that of families (₹110). One price either loses students or leaves money on the table with everyone else. A ₹49 tier is still profitable (₹24/member/month at students' order frequency), but only if non-students can't trade down. ID verification is the requirement that makes the tier viable.

## D7. Price tests by city cluster

See the [GTM plan](GO_TO_MARKET.md#why-test-prices-by-city-cluster-not-by-user). Fairness and trust outweigh the statistical efficiency of user-level randomisation for price.
