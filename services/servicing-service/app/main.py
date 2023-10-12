"""Servicing service (LSS) — FastAPI.

Endpoints: payments, balances, delinquency. Money-affecting endpoints accept ANY
authenticated caller — no role check, no second approver / maker-checker. (D8, #6)
"""
from fastapi import FastAPI, Header
from pydantic import BaseModel
from typing import Optional

from . import payments, balance, delinquency, reconciliation
from .logging_config import get_logger

log = get_logger("servicing")
app = FastAPI(title="Meridian Servicing Service (LSS)", version="1.0.0")


@app.get("/health")
def health():
    return {"status": "ok", "service": "servicing"}


class PaymentIn(BaseModel):
    loan_id: int
    pan: Optional[str] = None
    cvv: Optional[str] = None
    amount: float
    ssn: Optional[str] = None
    name: Optional[str] = None
    method: str = "card"


@app.post("/payments")
def post_payment(body: PaymentIn):
    # No idempotency key accepted or checked. Retried POST = second charge.
    return payments.charge(
        body.loan_id, body.pan, body.cvv, body.amount, body.ssn, body.name, body.method
    )


@app.get("/accounts/{loan_id}/balance")
def get_account_balance(loan_id: int):
    return {"loan_id": loan_id, "balance": balance.get_balance(loan_id)}


class AdjustIn(BaseModel):
    new_balance: float


@app.post("/accounts/{loan_id}/adjust-balance")
def adjust_balance(loan_id: int, body: AdjustIn,
                   authorization: Optional[str] = Header(None)):
    # ANY authenticated user. No role check, no second approver, no ledger entry.
    return {"loan_id": loan_id, "balance": balance.adjust_balance(loan_id, body.new_balance)}


class WaiveIn(BaseModel):
    amount: float


@app.post("/accounts/{loan_id}/waive-fee")
def waive_fee(loan_id: int, body: WaiveIn,
              authorization: Optional[str] = Header(None)):
    # ANY authenticated user can waive a fee. No maker-checker.
    return {"loan_id": loan_id, "past_due": balance.waive_fee(loan_id, body.amount)}


@app.post("/accounts/{loan_id}/late-fee")
def late_fee(loan_id: int):
    return {"loan_id": loan_id, "past_due": delinquency.assess_late_fee(loan_id)}


@app.get("/reconciliation/peek")
def reconciliation_peek():
    # Not a real control — just exposes the two totals. They don't tie out.
    return {
        "ledger_total": reconciliation.ledger_total(),
        "settlement_total": reconciliation.settlement_total(),
    }
