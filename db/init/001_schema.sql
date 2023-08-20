-- Meridian Lending — schema (Halcyon v1)
-- NOTE: money is stored as double precision throughout. Keeps the app code simple.

CREATE TABLE IF NOT EXISTS applicants (
    id          SERIAL PRIMARY KEY,
    name        TEXT NOT NULL,
    dob         DATE,
    ssn         TEXT,            -- plaintext
    ein         TEXT,            -- for entity applicants
    is_entity   BOOLEAN DEFAULT FALSE,
    address     TEXT,
    created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS applications (
    id              SERIAL PRIMARY KEY,
    applicant_id    INTEGER REFERENCES applicants(id),
    amount          DOUBLE PRECISION NOT NULL,   -- money as float
    term_months     INTEGER NOT NULL,
    purpose         TEXT,
    income          DOUBLE PRECISION,            -- money as float
    status          TEXT DEFAULT 'submitted',
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- KYC: CIP only. No sanctions/OFAC, no beneficial owner, no monitoring.
CREATE TABLE IF NOT EXISTS kyc_checks (
    id              SERIAL PRIMARY KEY,
    applicant_id    INTEGER REFERENCES applicants(id),
    name_verified   BOOLEAN,
    dob_verified    BOOLEAN,
    address_verified BOOLEAN,
    ssn_verified    BOOLEAN,
    -- no sanctions_screened, no ubo_identified, no ongoing_monitoring columns
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- Decision: OUTCOME ONLY. No reason, no model drivers, no inputs, no timestamp of model run.
CREATE TABLE IF NOT EXISTS decisions (
    app_id      INTEGER PRIMARY KEY REFERENCES applications(id),
    outcome     TEXT NOT NULL   -- 'approve' | 'deny' | 'refer' | 'counteroffer'
);

CREATE TABLE IF NOT EXISTS offers (
    id          SERIAL PRIMARY KEY,
    app_id      INTEGER REFERENCES applications(id),
    apr         DOUBLE PRECISION,    -- float APR (rounding risk)
    finance_charge DOUBLE PRECISION, -- float
    monthly_payment DOUBLE PRECISION,
    amount_financed DOUBLE PRECISION,
    total_of_payments DOUBLE PRECISION,
    created_at  TIMESTAMPTZ DEFAULT now()
);

-- LSS tables. A funded loan is "boarded" here by a direct insert from origination.
CREATE TABLE IF NOT EXISTS loans (
    id              SERIAL PRIMARY KEY,
    app_id          INTEGER,
    applicant_name  TEXT,
    principal       DOUBLE PRECISION NOT NULL,   -- money as float
    apr             DOUBLE PRECISION NOT NULL,
    term_months     INTEGER NOT NULL,
    status          TEXT DEFAULT 'current',
    opened_at       TIMESTAMPTZ DEFAULT now()
);

-- Mutable balance: one column, overwritten in place. No ledger, no transaction history.
CREATE TABLE IF NOT EXISTS balances (
    loan_id     INTEGER PRIMARY KEY REFERENCES loans(id),
    balance     DOUBLE PRECISION NOT NULL,   -- money as float, UPDATE-d in place
    past_due    DOUBLE PRECISION DEFAULT 0,
    updated_at  TIMESTAMPTZ DEFAULT now()
);

-- Payments: stores full PAN + CVV. No idempotency key. No unique charge reference.
CREATE TABLE IF NOT EXISTS payments (
    id          SERIAL PRIMARY KEY,
    loan_id     INTEGER REFERENCES loans(id),
    pan         TEXT,                 -- full PAN stored
    cvv         TEXT,                 -- CVV stored (SAD — flat PCI prohibition)
    amount      DOUBLE PRECISION NOT NULL,  -- money as float
    method      TEXT DEFAULT 'card',
    created_at  TIMESTAMPTZ DEFAULT now()
    -- no idempotency_key, no unique(charge_ref)
);

-- "audit" log: an ordinary, mutable table. Rows can be UPDATE/DELETE-d. Not append-only.
CREATE TABLE IF NOT EXISTS audit_logs (
    id          SERIAL PRIMARY KEY,
    actor       TEXT,
    action      TEXT,
    detail      TEXT,
    deleted_at  TIMESTAMPTZ,        -- soft-delete column on an "audit" trail
    created_at  TIMESTAMPTZ DEFAULT now()
);
