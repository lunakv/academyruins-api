from sqlalchemy import Column, Date, Integer, Text

from models import Base


class Ipg(Base):
    __tablename__ = "ipg"

    id = Column(Integer, primary_key=True)
    creation_day = Column(Date, index=True)
    file_name = Column(Text)
