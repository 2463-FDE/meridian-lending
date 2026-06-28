"""Application intake, listing, detail, decisioning, and acceptance/boarding."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import db, decision, intake, kyc, models
from ..database import get_session
from ..logging_config import get_logger
from ..schemas import (
    ApplicationCreated,
    ApplicationDetail,
    ApplicationIn,
    ApplicationListItem,
    ApplicantOut,
    DecisionOut,
    Disclosure,
    KycOut,
    Page,
)

log = get_logger("applications")
router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("", response_model=ApplicationCreated)
def submit_application(body: ApplicationIn):
    payload = body.model_dump()
    app_id = intake.create_application(payload)
    cip = kyc.run_cip(payload)  # CIP only — no sanctions / UBO / monitoring (debt)
    # persist the CIP result (still no sanctions/ubo columns to persist — debt preserved)
    try:
        applicant_rows = db.query(
            "SELECT applicant_id FROM applications WHERE id = %s", (app_id,)
        )
        applicant_id = applicant_rows[0]["applicant_id"] if applicant_rows else None
        db.query(
            "INSERT INTO kyc_checks (applicant_id, name_verified, dob_verified, "
            "address_verified, ssn_verified) VALUES (%s, %s, %s, %s, %s)",
            (applicant_id, cip["name_verified"], cip["dob_verified"],
             cip["address_verified"], cip["ssn_verified"]),
        )
    except Exception as e:  # noqa
        log.warning("could not persist kyc: %s", e)
    return {"app_id": app_id, "status": "submitted", "kyc": KycOut(**cip)}


@router.get("", response_model=Page[ApplicationListItem])
def list_applications(
    session: Session = Depends(get_session),
    status: str | None = Query(default=None),
    limit: int = Query(default=25, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    stmt = select(models.Application, models.Applicant.name).join(
        models.Applicant, models.Application.applicant_id == models.Applicant.id, isouter=True
    )
    count_stmt = select(func.count(models.Application.id))
    if status:
        stmt = stmt.where(models.Application.status == status)
        count_stmt = count_stmt.where(models.Application.status == status)
    total = session.scalar(count_stmt) or 0
    stmt = stmt.order_by(models.Application.id.desc()).limit(limit).offset(offset)
    items = [
        ApplicationListItem(
            id=a.id, applicant_name=name, amount=a.amount, term_months=a.term_months,
            purpose=a.purpose, status=a.status,
            created_at=a.created_at.isoformat() if a.created_at else None,
        )
        for a, name in session.execute(stmt).all()
    ]
    return Page(items=items, total=total, limit=limit, offset=offset)


@router.get("/{app_id}", response_model=ApplicationDetail)
def get_application(app_id: int, session: Session = Depends(get_session)):
    a = session.get(models.Application, app_id)
    if not a:
        raise HTTPException(status_code=404, detail="application not found")
    applicant = a.applicant
    kyc_row = session.scalar(
        select(models.KycCheck).where(models.KycCheck.applicant_id == a.applicant_id)
        .order_by(models.KycCheck.id.desc())
    ) if a.applicant_id else None
    dec = session.get(models.Decision, app_id)
    offer = session.scalar(
        select(models.Offer).where(models.Offer.app_id == app_id).order_by(models.Offer.id.desc())
    )
    return ApplicationDetail(
        id=a.id,
        applicant=ApplicantOut(
            id=applicant.id, name=applicant.name, email=applicant.email,
            phone=applicant.phone, address=applicant.address, is_entity=applicant.is_entity,
        ) if applicant else None,
        amount=a.amount, term_months=a.term_months, purpose=a.purpose, status=a.status,
        employer=a.employer, job_title=a.job_title,
        kyc=KycOut(
            name_verified=bool(kyc_row.name_verified), dob_verified=bool(kyc_row.dob_verified),
            address_verified=bool(kyc_row.address_verified), ssn_verified=bool(kyc_row.ssn_verified),
        ) if kyc_row else None,
        decision=dec.outcome if dec else None,
        offer=Disclosure(
            apr=offer.apr or 0, finance_charge=offer.finance_charge or 0,
            monthly_payment=offer.monthly_payment or 0, amount_financed=offer.amount_financed or 0,
            total_of_payments=offer.total_of_payments or 0,
        ) if offer else None,
    )


@router.post("/{app_id}/decision", response_model=DecisionOut)
def run_decision(app_id: int):
    rows = db.query(
        "SELECT a.id, a.income, ap.ssn FROM applications a "
        "LEFT JOIN applicants ap ON ap.id = a.applicant_id WHERE a.id = %s",
        (app_id,),
    )
    if not rows:
        raise HTTPException(status_code=404, detail="application not found")
    application = {"app_id": app_id, "ssn": rows[0].get("ssn") or "", "income": rows[0].get("income") or 0}
    result = decision.decide(application)  # synchronous chain; persists outcome only (debt)
    return DecisionOut(
        app_id=app_id, decision=result["decision"], score=result["score"],
        adverse_action_reason=result.get("adverse_action_reason"),
    )


@router.post("/{app_id}/accept")
def accept_offer(app_id: int):
    rows = db.query(
        "SELECT a.amount, a.term_months, ap.name, o.apr "
        "FROM applications a LEFT JOIN applicants ap ON ap.id = a.applicant_id "
        "LEFT JOIN offers o ON o.app_id = a.id WHERE a.id = %s ORDER BY o.id DESC",
        (app_id,),
    )
    if not rows:
        raise HTTPException(status_code=404, detail="application not found")
    r = rows[0]
    rate = r.get("apr") or 7.99
    loan_id = intake.board_to_servicing(
        app_id, r.get("name") or "Borrower", r["amount"], rate, r["term_months"]
    )
    db.query("UPDATE applications SET status = 'funded' WHERE id = %s", (app_id,))
    return {"loan_id": loan_id}
