# Meridian Lending Platform

> **SOC 2 Type II / SOX-controlled. Cardholder data is encrypted and we are PCI-DSS compliant. Every credit decision is audited.**

The Meridian Lending Co. loan origination + servicing platform. Originally delivered by
Halcyon Software Group (now dissolved); maintained in-house since 2024-Q4.

This is a brownfield monorepo: a **Loan Origination System (LOS)** and a **Loan Servicing
System (LSS)** bolted together behind a single API gateway, with a Next.js portal and a
half-finished "AI underwriting assistant" the previous vendor started.

## Architecture

```
                          ┌──────────────────────┐
  Next.js portal  ───────►│   gateway (BFF)      │  :8000
  (apply + servicing)     └─────────┬────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        ▼                           ▼                           ▼
 origination-service        servicing-service           ai-orchestrator
   :8001  (LOS)               :8002  (LSS)                :8003
   intake / KYC /             payments / balances /        Bedrock summary
   decisioning /              delinquency                   assistant (WIP)
   disclosure
        │                           │                           │
        └──────────────┬────────────┴───────────────────────────┘
                       ▼
              Postgres :5432   +   Redis :6379
```

The LOS↔LSS **seam** is thin and undocumented — a loan "boards" from origination to
servicing by a direct insert into the servicing schema. See `docs/architecture.md`.

## Quick start

```bash
cp .env.example .env     # the real .env is already in the repo so you can just run it
make up                  # docker compose up -d (postgres, redis, all services, frontend)
make logs                # tail everything
make seed                # load db/init seed data (loans, payments, decisions)
make down
```

Portal: http://localhost:3000  ·  Gateway: http://localhost:8000/docs

## Services

| Path | Service | Port | Notes |
|------|---------|------|-------|
| `frontend/` | Next.js 15 portal | 3000 | application intake + servicing dashboard |
| `services/gateway/` | FastAPI BFF | 8000 | routes to LOS/LSS/AI |
| `services/origination-service/` | FastAPI (LOS) | 8001 | intake, KYC, decisioning, disclosure |
| `services/servicing-service/` | FastAPI (LSS) | 8002 | payments, balances, delinquency |
| `services/ai-orchestrator/` | FastAPI | 8003 | Bedrock loan-summary assistant (half-built) |
| `db/` | Postgres init + seed | 5432 | schema, migrations, seed data |

## Compliance

We are PCI-DSS compliant (cardholder data encrypted), SOX-controlled with full audit
trails on financial actions, and follow ECOA/Reg B for all adverse-action notices.
Compliance contact: Dana (VP Lending Ops). For SOX/reconciliation questions: Sam
(Controller). For fair-lending/BSA: Priya (Compliance Officer).

## Known follow-ups (from the Halcyon handoff note)

> "Platform is secure and compliant. A few TODOs left in servicing and the AI box but
> nothing blocking. — Halcyon"
