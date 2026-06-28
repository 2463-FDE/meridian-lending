# Meridian Lending — Architecture

> Maintained by the in-house team. The platform was originally delivered by Halcyon
> Software Group (dissolved) and has been extended in-place since. Treat this as the
> current best understanding, not a clean-room design.

## System shape

Meridian is a consumer **personal-installment-loan** platform: two domains (origination
and servicing) bolted together behind one BFF gateway, with a Next.js portal.

```
 Borrower / Servicing Rep ─► Next.js portal (3000)
                                   │  Authorization: Bearer <session>
                                   ▼
                          gateway / BFF (8000)  ── Redis (sessions)
                          /auth · /los · /lss
                     ┌───────────┴────────────┐
                     ▼                         ▼
        origination-service (8001)   servicing-service (8002)
        LOS: intake, KYC (CIP),      LSS: loans, balances,
        decisioning, disclosure      payments, schedule, delinquency
                     └───────────┬────────────┘
                                 ▼
                           Postgres (5432)
```

## Services

| Service | Tech | Responsibility |
|---------|------|----------------|
| `gateway` | FastAPI + httpx + Redis | Session auth (`/auth/*`), role forwarding, reverse-proxy to `/los/*` and `/lss/*`. |
| `origination-service` (LOS) | FastAPI + SQLAlchemy + psycopg2 | Application intake & listing, KYC (CIP), credit decisioning, TILA disclosure/offer, LOS→LSS boarding seam. |
| `servicing-service` (LSS) | FastAPI + SQLAlchemy + psycopg2 | Loan portfolio, balances, amortization schedule, payments, delinquency/late fees, reconciliation peek. |
| `frontend` | Next.js 15 (App Router) | Borrower application wizard, offer/disclosure screen, servicing dashboard + loan detail. |

### Data access — a partial ORM migration

Read paths (loan/application listing, detail, schedule, payment history) use **SQLAlchemy
2.0** ORM models (`models.py` + `database.py`). The older money-moving write paths
(`intake.py`, `decision.py`, `payments.py`, `balance.py`) still use **raw psycopg2**
(`db.py`). The migration to the ORM was never finished — this seam is intentional and is
where most of the money-handling debt lives.

## Auth & roles

`users` table holds staff + borrower logins (`admin`, `underwriter`, `csr`, `borrower`).
Login → unsalted-sha256 password check → opaque token in Redis (`session:<token>`, 8h
TTL). The gateway resolves the session and forwards `X-User-Id` / `X-User-Role`.
Downstream services accept those headers and **do not enforce role** on balance
adjustments or fee waivers.

## Data model (Postgres)

`users`, `applicants`, `applications`, `kyc_checks`, `decisions`, `offers`, `loans`,
`balances`, `payments`, `audit_logs`. Authoritative DDL: `db/init/001_schema.sql`. Seed:
`db/init/002_seed.sql` (curated anchors) + `db/init/003_seed_bulk.sql` (synthetic
portfolio of ~300 applications / ~180 loans / ~600 payments). Migrations under
`db/migrations/` are hand-tracked and lag the init DDL.

Money is stored as `DOUBLE PRECISION` throughout. `balances` is a single mutable column
(no ledger). `decisions` records the outcome only. `payments` carries the full PAN + CVV
and has no idempotency key. See ADR 0002 / 0003 for the original rationale.

## The LOS↔LSS seam

A funded loan is "boarded" by a direct cross-schema `INSERT` from origination into the
servicing `loans` + `balances` tables (`origination-service/app/intake.py::board_to_servicing`).
No boarding API, event, or contract. ADR 0002.

## Local development

`docker compose up -d` brings up Postgres (auto-seeds from `db/init`), Redis, both
backend services, the gateway, and the frontend. See `docs/runbook.md`.
