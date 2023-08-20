# ADR 0002: One Postgres database shared by origination and servicing

- **Status:** Accepted
- **Date:** 2023-09-02
- **Author:** Halcyon Software Group

## Context

We are shipping both a Loan Origination System (LOS) and a Loan Servicing System (LSS).
The sales timeline requires a working end-to-end demo in six weeks.

## Decision

Both services will share **one** Postgres database and read/write each other's tables
directly. "Boarding" a funded loan from LOS to LSS will be a direct `INSERT` into the
servicing tables from the origination code path — no boarding API or event.

## Consequences

- **Pro:** fastest path to a working demo; no integration contract to maintain.
- **Con:** the LOS/LSS boundary is a fiction; a schema change in one service can break
  the other silently. There is no provenance for how a loan moved between systems.
- We accept this for v1. (Revisit "if we ever scale." — never revisited.)
