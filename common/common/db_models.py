import uuid
from datetime import datetime
from os import environ

from sqlalchemy import Column, Integer, String, UUID, DateTime, ForeignKey, Boolean
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship

Base = declarative_base()


class Event(Base):
    __tablename__ = 'events'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(30), unique=True, nullable=False)
    date = Column(DateTime, nullable=False)
    location = Column(String)
    participants_num = Column(Integer)
    creation_date = Column(DateTime, default=datetime.now())
    deleted = Column(Boolean, default=False)

    subscribers_relation = relationship('EventSubscriber', back_populates='events_relation', cascade='all, delete-orphan')


class EventSubscriber(Base):
    __tablename__ = 'event_subscribers'

    user_id = Column(UUID(as_uuid=True), primary_key=True)
    event_id = Column(UUID(as_uuid=True), ForeignKey('events.id', ondelete='CASCADE'), primary_key=True)

    events_relation = relationship('Event', back_populates='subscribers_relation')


postgres_url = environ['DB_URI']
engine = create_engine(postgres_url)
Base.metadata.create_all(engine)


def create_db_session() -> scoped_session:
    return scoped_session(sessionmaker(bind=engine))
