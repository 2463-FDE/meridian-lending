"""Payment handling (formerly the vendor's prototype 'pay.py').

Stores the FULL PAN and the CVV on the payments row. Logs the full charge request
(PAN, CVV, SSN) at INFO. There is NO idempotency key — a retried POST inserts a second
payments row and applies the amount twice (double-charge). (D2, D5, #4, #7)
"""
from .logging_config import get_logger
from . import db, balance

log = get_logger("payment")   # writes to logs/payment-service.log


def charge(loan_id: int, pan: str, cvv: str, amount: float, ssn: str = None,
           name: str = None, method: str = "card") -> dict:
    # Full request body — including PAN, CVV, SSN — at INFO. No redaction.
    log.info(
        'POST /payments charge req={"pan":"%s","cvv":"%s","ssn":"%s","amount":%s,'
        '"loan_id":%s,"name":"%s"} -> ok',
        pan, cvv, ssn, amount, loan_id, name,
    )
    # No idempotency check. No unique charge reference. Every POST inserts a row.
    db.query(
        "INSERT INTO payments (loan_id, pan, cvv, amount, method) "
        "VALUES (%s, %s, %s, %s, %s)",
        (loan_id, pan, cvv, float(amount), method),   # full PAN + CVV persisted
    )
    new_balance = balance.apply_payment(loan_id, amount)
    return {"loan_id": loan_id, "amount": amount, "balance": new_balance}
