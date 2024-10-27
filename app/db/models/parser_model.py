from sqlalchemy import ARRAY, TIMESTAMP, VARCHAR, Column, Text, BigInteger, func
from .. import Base


class ParserModel(Base):
    __tablename__ = "parser"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    description = Column(Text, nullable=False)
    imgs = Column(ARRAY(VARCHAR), nullable=True)
    datetime = Column(TIMESTAMP, server_default=func.now(), nullable=False)
