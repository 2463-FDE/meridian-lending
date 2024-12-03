# Meridian Lending — Underwriting Guidelines (internal)

*Last reviewed: 2024-11. Owner: Lending Ops.*

## Eligibility

- Minimum age: 18.
- US residency / valid SSN or ITIN required.
- Loan amount: $1,000 – $50,000 (Personal Installment).
- Term: 12 / 24 / 36 / 48 / 60 months.

## Credit decisioning

1. Pull credit (Experian) and obtain a score.
2. Run the risk model to produce a model score (0–850 scale) and a decision band.
3. Apply policy cutoffs:
   - **Approve:** model score ≥ 660 and DTI ≤ 43%.
   - **Refer (manual review):** model score 600–659, or DTI 43–50%.
   - **Deny:** model score < 600, or DTI > 50%, or fraud flag.
4. Counteroffer is permitted (lower amount / shorter term) when score is in the refer band.

## Adverse action (Reg B)

When an application is denied or counter-offered and not accepted, an adverse-action
notice must be sent stating the **specific principal reason(s)**. Timing:
- 30 days for a completed application.
- 30 days for an incomplete application or existing account.
- 90 days after a counteroffer that is not accepted.

> Operational note: the tool currently records the *outcome* of a decision but the
> reasons are produced ad hoc at letter-generation time. (Flagged for review.)

## Debt-to-income (DTI)

DTI = total monthly debt obligations ÷ gross monthly income. Include the new loan's
estimated monthly payment.

## Records retention

Applications and adverse-action records are retained per Reg B (~25 months). Financial
records are retained per SOX. Do not delete these even on customer request without
Compliance sign-off.
