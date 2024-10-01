from sqlalchemy import BigInteger, Text, VARCHAR, ARRAY, Date, Boolean, Column
from backend.database import Base


class UserDB(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True, nullable=False)
    username = Column(VARCHAR, nullable=False)
    email = Column(VARCHAR, nullable=False)
    password_hash = Column(VARCHAR, nullable=False)


class PostDB(Base):
    __tablename__ = "posts"
    id = Column(BigInteger, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    imgs = Column(ARRAY(Text), nullable=False)
    date = Column(Date, nullable=False)
