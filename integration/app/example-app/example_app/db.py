import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("postgresql://me:veryinsecure@primary/mydb")

Session = sessionmaker(engine)
