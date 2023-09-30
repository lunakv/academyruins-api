from sqlalchemy import Column, Text

from models import Base


class Redirect(Base):
    __tablename__ = "redirects"

    resource = Column(Text, primary_key=True)
    link = Column(Text, nullable=False)


class PendingRedirect(Base):
    __tablename__ = "redirects_pending"

    resource = Column(Text, primary_key=True)
    link = Column(Text, nullable=False)
