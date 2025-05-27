from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from qrcode_db import QRCode, QRType, get_db


router = APIRouter()

# Pydantic request model
class QRCodeCreate(BaseModel):
    user_name: str
    code: str
    duration_minutes: int = None  # Only for limited QR codes

# Helper to create QR code
def create_qr_code(session: Session, user_name: str, code: str, qr_type: QRType, duration_minutes: int = None):
    expires_at = None
    if qr_type == QRType.limited and duration_minutes:
        expires_at = datetime.utcnow() + timedelta(minutes=duration_minutes)
    elif qr_type == QRType.one_time:
        expires_at = datetime.utcnow() + timedelta(days=1)

    qr = QRCode(
        user_name=user_name,
        code=code,
        type=qr_type,
        expires_at=expires_at
    )
    session.add(qr)
    session.commit()
    return qr

# POST /create/permanent
@router.post("/create/permanent")
def create_permanent_qr(qr_data: QRCodeCreate, db: Session = Depends(get_db)):
    qr = create_qr_code(db, qr_data.user_name, qr_data.code, QRType.permanent)
    return {"message": "Permanent QR code created.", "qr_code": qr.code}

# POST /create/limited
@router.post("/create/limited")
def create_limited_qr(qr_data: QRCodeCreate, db: Session = Depends(get_db)):
    if not qr_data.duration_minutes:
        raise HTTPException(status_code=400, detail="duration_minutes is required for limited QR code.")
    qr = create_qr_code(db, qr_data.user_name, qr_data.code, QRType.limited, qr_data.duration_minutes)
    return {"message": "Limited QR code created.", "qr_code": qr.code}

# POST /create/one_time
@router.post("/create/one_time")
def create_one_time_qr(qr_data: QRCodeCreate, db: Session = Depends(get_db)):
    qr = create_qr_code(db, qr_data.user_name, qr_data.code, QRType.one_time)
    return {"message": "One-time QR code created.", "qr_code": qr.code}

# # GET /qr/{code}
# @router.get("/qr/{code}")
# def get_qr(code: str, db: Session = Depends(get_db)):
#     qr = db.query(QRCode).filter_by(code=code).first()
#     if not qr:
#         raise HTTPException(status_code=404, detail="QR code not found.")

#     # Handle limited QR expiration
#     if qr.type == QRType.limited and qr.expires_at and qr.expires_at < datetime.utcnow():
#         raise HTTPException(status_code=400, detail="QR code has expired.")

#     # Handle one-time QR deletion
#     if qr.type == QRType.one_time:
#         db.delete(qr)
#         db.commit()

#     return {
#         "user_name": qr.user_name,  # Directly access user_name
#         "code": qr.code,
#         "type": qr.type.value,
#         "expires_at": qr.expires_at,
#     }

# GET /qr/all
@router.get("/qr/all")
def get_all_qrs(db: Session = Depends(get_db)):
    qr_codes = db.query(QRCode).all()
    return [
        {
            "index": i,
            "user_name": qr.user_name,
            "code": qr.code,
            "type": qr.type.value,
            "expires_at": qr.expires_at,
        }
        for i, qr in enumerate(qr_codes)
    ]

# DELETE /qr/delete/{index}
@router.delete("/qr/delete/{index}")
def delete_qr_by_index(index: int, db: Session = Depends(get_db)):
    qr_list = db.query(QRCode).all()
    if index < 0 or index >= len(qr_list):
        raise HTTPException(status_code=404, detail="Invalid QR code index.")

    qr_to_delete = qr_list[index]
    db.delete(qr_to_delete)
    db.commit()
    return {"message": f"QR code '{qr_to_delete.code}' deleted."}
