from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Enum
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timedelta
import enum

Base = declarative_base()

# Enum for QR code types
class QRType(enum.Enum):
    permanent = "permanent"
    limited = "limited"
    one_time = "one-time"

# QR code table (with user_name directly stored)
class QRCode(Base):
    __tablename__ = 'qr_codes'
    id = Column(Integer, primary_key=True)
    user_name = Column(String, nullable=False)
    code = Column(String, unique=True, nullable=False)
    type = Column(Enum(QRType), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    used = Column(Boolean, default=False)

    def __repr__(self):
        return f"<QRCode(user={self.user_name}, code={self.code}, type={self.type})>"

# Setup database
engine = create_engine('sqlite:///qrcodes.db')
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base.metadata.create_all(engine)

# Add QR code with user name
def add_qr_code(session, user_name, code, qr_type, duration_minutes=None):
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

# Get QR code (handle one-time and expiration logic)
def get_qr_code(session, code):
    qr = session.query(QRCode).filter_by(code=code).first()
    if qr:
        if qr.type == QRType.limited and qr.expires_at and qr.expires_at < datetime.utcnow():
            print("QR code has expired.")
            return None

        if qr.type == QRType.one_time:
            print(f"One-time QR used. Deleting: {qr.code}")
            session.delete(qr)
            session.commit()
            return qr

        return qr
    return None

# Get all QR codes
def get_all_qr_codes(session):
    return session.query(QRCode).all()

# Delete QR code by index
def delete_qr_code_by_index(session, index):
    qr_codes = get_all_qr_codes(session)
    if 0 <= index < len(qr_codes):
        to_delete = qr_codes[index]
        print(f"Deleting: {to_delete}")
        session.delete(to_delete)
        session.commit()
        return True
    else:
        print("Invalid index.")
        return False

# Session dependency (e.g. for FastAPI)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Example usage
if __name__ == "__main__":
    session = SessionLocal()

    # Add example QR codes (run only once)
    # add_qr_code(session, "Alice", "QR_PERM_001", QRType.permanent)
    # add_qr_code(session, "Bob", "QR_LIMIT_001", QRType.limited, duration_minutes=5)
    # add_qr_code(session, "Charlie", "QR_ONE_001", QRType.one_time)

    print("\nAll QR Codes:")
    qr_codes = get_all_qr_codes(session)
    for i, qr in enumerate(qr_codes):
        print(f"[{i}] {qr.user_name} - {qr.code} - {qr.type.value} - Expires at: {qr.expires_at}")
        # print(f"[{i}] {qr.user_name} - {qr.code} - {qr.type}")

    # # Delete QR code by index
    # index_to_delete = 0
    # print(f"\nAttempting to delete QR code at index {index_to_delete}...")
    # if delete_qr_code_by_index(session, index_to_delete):
    #     print("QR code deleted.")
    # else:
    #     print("Failed to delete QR code.")
