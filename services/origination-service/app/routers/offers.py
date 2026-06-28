"""Offer / Truth-in-Lending disclosure generation."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import intake, models, schedule
from ..database import get_session
from ..schemas import Disclosure, OfferOut, ScheduleRow

router = APIRouter(tags=["offers"])


class OfferIn(BaseModel):
    app_id: int
    principal: float = Field(gt=0, le=50000)
    annual_rate_pct: float = Field(default=7.99, gt=0, le=35)
    term_months: int = Field(default=48, ge=12, le=60)


@router.post("/offer", response_model=OfferOut)
def make_offer(body: OfferIn):
    o = intake.build_disclosure(body.app_id, body.principal, body.annual_rate_pct,
                                body.term_months)
    rows = schedule.amortization(body.principal, body.annual_rate_pct, body.term_months)
    disclosure = Disclosure(
        apr=o["apr"], finance_charge=o["finance_charge"], monthly_payment=o["monthly_payment"],
        amount_financed=o["amount_financed"], total_of_payments=o["total_of_payments"],
        schedule=[ScheduleRow(**r) for r in rows],
    )
    return OfferOut(app_id=body.app_id, disclosure=disclosure)


@router.get("/applications/{app_id}/offer", response_model=OfferOut)
def get_offer(app_id: int, session: Session = Depends(get_session)):
    offer = session.scalar(
        select(models.Offer).where(models.Offer.app_id == app_id).order_by(models.Offer.id.desc())
    )
    if not offer:
        raise HTTPException(status_code=404, detail="no offer for this application")
    app_row = session.get(models.Application, app_id)
    rows = []
    if app_row:
        rows = schedule.amortization(app_row.amount, offer.apr or 7.99, app_row.term_months)
    disclosure = Disclosure(
        apr=offer.apr or 0, finance_charge=offer.finance_charge or 0,
        monthly_payment=offer.monthly_payment or 0, amount_financed=offer.amount_financed or 0,
        total_of_payments=offer.total_of_payments or 0,
        schedule=[ScheduleRow(**r) for r in rows],
    )
    return OfferOut(app_id=app_id, disclosure=disclosure)
