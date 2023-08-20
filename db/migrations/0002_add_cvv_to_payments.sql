-- 0002 — store CVV on payments so finance can re-run a charge (see ADR 0003)
-- Applied 2023-10.
ALTER TABLE payments ADD COLUMN IF NOT EXISTS cvv TEXT;
