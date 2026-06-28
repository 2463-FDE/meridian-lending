# Meridian Lending — Architecture Notes

*(Reconstructed by the in-house team after Halcyon dissolved. Incomplete.)*

## The two halves (the "seam")

Meridian is really **two systems bolted together**:

- **LOS — Loan Origination System** (`origination-service`): everything up to funding.
  application intake → KYC (CIP) → credit pull + decisioning → disclosure/offer.
- **LSS — Loan Servicing System** (`servicing-service`): everything after funding.
  payments → balances → delinquency/late fees.

```
  applicant ──► frontend ──► gateway ──► origination-service (LOS)
                                              │
                                              │  "boarding" — a loan that is
                                              ▼  approved+funded is handed to LSS
                                        servicing-service (LSS)
                                              │
                                              ▼
                                          Postgres
```

### The seam is undocumented and direct

When a loan is approved and funded, origination "boards" it to servicing by writing
directly into the servicing tables (`loans`, `balances`) — there is no boarding API,
no event, no contract. The two services share one Postgres database and reach across
each other's schemas. See `origination-service/app/intake.py::board_to_servicing`.

This is **brownfield seam #1**: the systems were integrated by a sales-driven vendor
to "make the demo work," not designed.

## Data stores

- **Postgres** — users, applicants, applications, kyc_checks, decisions, offers, loans,
  balances, payments, audit_logs.
- **Redis** — login sessions (gateway). Also intended for idempotency keys / jobs —
  never wired up.

## Auth

The gateway handles login (`/auth/*`) against the `users` table, mints an opaque session
token stored in Redis, and forwards the resolved identity downstream as `X-User-*`
headers. Downstream services trust those headers and do **not** re-check role on
money-moving actions (the weak-authz gap).

## External integrations

- **Experian** — credit pull (key hardcoded in `origination-service/app/config.py`).
- **Card/ACH processor** — payments (`servicing-service`).

## Known unknowns (things the team has not had time to map)

- How balances are recomputed after a partial payment + a fee waiver on the same day.
- Whether the processor settlement file actually ties out to the `payments` table.
- Where adverse-action *reasons* are stored (we think… nowhere?).
- Whether any servicing action is actually restricted by role.
