from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "public"}
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    nickname = Column(String)
