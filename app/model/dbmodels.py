# coding: utf-8
from sqlalchemy import Column, Integer, Text, text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Event(Base):
    __tablename__ = 'Events'

    ID = Column(Integer, primary_key=True)
    AppKey = Column(Text)
    EventCode = Column(Text)
    EventName = Column(Text)
    Create_Time = Column(Text, server_default=text("STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW')"))
    Update = Column(Text, server_default=text("STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW')"))
