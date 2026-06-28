# Meridian Lending — Operations Runbook

> In-house ops notes. Sparse — Halcyon left no runbook, so this is what we've pieced
> together. Add to it when you learn something the hard way.

## Local / dev bring-up

```bash
cp .env.example .env     # NOTE: a populated .env is already committed, so this is optional
make up                  # docker compose up -d --build (postgres, redis, services, frontend)
make logs                # tail all services
make ps                  # container status
make down                # stop everything
```

- Portal: http://localhost:3000
- Gateway + OpenAPI docs: http://localhost:8000/docs
- Postgres: localhost:5432 (`meridian` / see `.env`)
- The DB auto-seeds from `db/init/*.sql` on first `up` (fresh volume only).

To re-apply the curated seed without recreating the volume:
```bash
make seed
```

To wipe and re-seed from scratch:
```bash
docker compose down -v && make up
```

## Demo logins

All seeded with password `password`:

| Username | Role | Use |
|----------|------|-----|
| `admin` | admin | full portal |
| `underwriter` | underwriter | decisioning views |
| `csr` | csr | servicing dashboard |
| `maria` | borrower | borrower view (applicant #1) |

## Health checks

```bash
curl localhost:8000/health     # gateway
curl localhost:8001/health     # origination (LOS)
curl localhost:8002/health     # servicing (LSS)
```

## Common tasks

- **Run a credit decision:** `POST /los/applications/{id}/decision`.
- **Generate an offer/disclosure:** `POST /los/offer {app_id, principal, annual_rate_pct, term_months}`.
- **Board an approved app to servicing:** `POST /los/applications/{id}/accept`.
- **Look at the portfolio:** `GET /lss/loans?limit=25&offset=0&status=current` (requires auth).
- **Reconciliation eyeball:** `GET /lss/reconciliation/peek` (ledger vs settlement totals).

## Known operational pain (unresolved)

- **Payment retries.** The processor occasionally times out; clients retry. There is no
  idempotency key, so retried payments insert a second row and apply twice. We field
  "double charge" support tickets a few times a month. (No fix yet.)
- **Month-end close.** `reconciliation.peek` totals do not tie out and nothing runs on a
  schedule. Finance reconciles by hand in a spreadsheet.
- **Logs contain card + SSN data.** `logs/payment-service.log` has full PAN/CVV/SSN at
  INFO. Do not ship these logs to a third-party aggregator until redaction is added.
- **Secrets are in the repo.** `.env` is committed and `config.py` hardcodes fallbacks.
  Rotate before any real go-live. (Long-standing TODO.)

## Tests

```bash
make test    # runs pytest in both backend services (non-blocking)
```

Some money-math tests (`test_apr.py`, `test_money.py`) currently FAIL by design — they
encode the float-rounding defects we have not fixed. CI runs them `continue-on-error`.
