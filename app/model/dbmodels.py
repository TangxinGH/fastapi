# coding: utf-8
from sqlalchemy import CHAR, Column, Date, DateTime, Integer, String, Table, Text, text
from sqlalchemy.sql.sqltypes import NullType
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Event(Base):
    __tablename__ = 'Events'

    ID = Column(Integer, primary_key=True)
    AppKey = Column(Text)
    AppName = Column(Text)
    EventCode = Column(Text)
    EventName = Column(Text)
    Create_Time = Column(Text, server_default=text("STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW')"))
    Update = Column(Text, server_default=text("STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW')"))
    TimeStamp = Column(Date, server_default=text("CURRENT_TIMESTAMP"))


class Schedule(Base):
    __tablename__ = 'Schedules'

    ID = Column(Integer, primary_key=True)
    SchKey = Column(Text)
    SchName = Column(Text)
    How = Column(String)
    When = Column(Text)
    What = Column(Text)
    Minutes = Column(Text)
    Success_Code = Column(CHAR, server_default=text("404"))
    Fail_Code = Column(CHAR, server_default=text("200"))
    Create_Time = Column(DateTime, server_default=text("datetime ('now', 'localtime')"))
    Update_Time = Column(Text, server_default=text("datetime ('now', 'localtime')"))


class SchedulesWeb(Base):
    __tablename__ = 'Schedules_Web'

    ID = Column(Integer, primary_key=True)
    AppKey = Column(Text)
    AppName = Column(Text)
    How = Column(Text)
    When = Column(Text)
    What = Column(Text)
    Minutes = Column(Integer)
    Success_Code = Column(Text, server_default=text("200"))
    Fail_Code = Column(Text, server_default=text("404"))
    CreateTime = Column(Text, server_default=text("CURRENT_TIMESTAMP"))
    Update_Time = Column(Text, server_default=text("CURRENT_TIMESTAMP"))


t_sqlite_sequence = Table(
    'sqlite_sequence', metadata,
    Column('name', NullType),
    Column('seq', NullType)
)
