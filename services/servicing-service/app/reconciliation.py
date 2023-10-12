"""Reconciliation.

There is no reconciliation job. The ledger (payments) is never compared to the
processor settlement file (data/settlement.csv). This stub exists only so finance
could 'eyeball' a total; it is not run on a schedule and does not report breaks. (D7)
"""
import csv
import os
from .config import SETTLEMENT_FILE
from . import db


def ledger_total() -> float:
    rows = db.query("SELECT COALESCE(SUM(amount), 0) AS total FROM payments")
    return float(rows[0]["total"]) if rows else 0.0


def settlement_total() -> float:
    if not os.path.exists(SETTLEMENT_FILE):
        return 0.0
    total = 0.0
    with open(SETTLEMENT_FILE) as f:
        for row in csv.DictReader(f):
            amt = float(row["amount"])
            total += amt if row["type"] == "capture" else -amt
    return total

# NOTE: nothing calls these on a schedule. No break-report. No alert. (D7)
