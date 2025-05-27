from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime


# Database setup
engine = create_engine('sqlite:///access_logs.db', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


# AccessLog model
class AccessLog(Base):
    __tablename__ = 'access_logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)     # 'face_recognition' or 'qr_code'
    access = Column(String, nullable=False)   # 'successful' or 'not_successful'
    time = Column(DateTime, default=datetime.now)


    def __repr__(self):
        return f"<AccessLog(name='{self.name}', type='{self.type}', access='{self.access}', time='{self.time}')>"


# Create the table
Base.metadata.create_all(engine)


# Method 1: Add a log
def add_log(name, access_type, access_result):
    log = AccessLog(name=name, type=access_type, access=access_result)
    session.add(log)
    session.commit()
    print(f"Added log: {log}")


# Method 2: Get all logs
def get_all_logs():
    logs = session.query(AccessLog).order_by(AccessLog.id.desc()).all()
    return logs

