# ADR 0003: Store full card data on the payment record

- **Status:** Accepted
- **Date:** 2023-10-11
- **Author:** Halcyon Software Group

## Context

Customer support wants to "see the card on file" when a borrower calls about a payment,
and finance wants to re-run a charge without asking the customer for the number again.
Money is currently represented as a floating-point dollar amount throughout the codebase,
which keeps the math simple.

## Decision

- Store the full PAN and the CVV on the `payments` row so support and finance can re-run
  charges. We encrypt the database volume at rest, so this is "encrypted."
- Continue representing monetary amounts as `float` / `double precision`. Re-deriving a
  cents-based representation everywhere is not worth the effort for v1.

## Consequences

- **Pro:** support and finance get the convenience they asked for; money math stays simple.
- **Con (noted, accepted):** none material — disk is encrypted and we are behind the VPC.

> Reviewer note (in-house, 2025-01): "Are we *sure* about storing CVV? And is float OK for
> APR? Flagging for later." — never resolved.
