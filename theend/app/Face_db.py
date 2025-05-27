from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
import numpy as np

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    embeddings = relationship("Embedding", back_populates="user", cascade="all, delete-orphan")

class Embedding(Base):
    __tablename__ = 'embeddings'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    embedding = Column(LargeBinary, nullable=False)
    user = relationship("User", back_populates="embeddings")

class Database:
    def __init__(self, db_url='sqlite:///embeddings.db'):
        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def insert_embedding(self, username, embedding_array: np.ndarray):
        session = self.Session()
        user = session.query(User).filter_by(username=username).first()
        if not user:
            user = User(username=username)
            session.add(user)
            session.flush()  # so user.id is available

        emb = Embedding(user=user, embedding=embedding_array.tobytes())
        session.add(emb)
        session.commit()
        session.close()

    def get_all_embeddings(self):
        session = self.Session()
        embeddings = session.query(Embedding).all()
        X, y = [], []
        for emb in embeddings:
            arr = np.frombuffer(emb.embedding, dtype=np.float32)
            X.append(arr)
            y.append(emb.user.username)
        session.close()
        return X, y

    def delete_user(self, username):
        session = self.Session()
        user = session.query(User).filter_by(username=username).first()
        if user:
            session.delete(user)
            session.commit()
        session.close()

    def list_users(self):
        session = self.Session()
        return session.query(User.username).all()
