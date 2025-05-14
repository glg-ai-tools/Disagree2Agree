# Removed Flask dependency by initializing SQLAlchemy independently
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()
engine = create_engine('sqlite:///debate_forum.db')
Session = sessionmaker(bind=engine)
session = Session()

db = Base

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

class DebateTopic(db):
    __tablename__ = 'debate_topic'

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    creation_timestamp = Column(db.DateTime, default=datetime.utcnow)
    
    arguments = relationship('Argument', backref='topic', lazy=True)
    logs = relationship(
        'DebateLog',
        back_populates='topic',
        cascade='all, delete-orphan',
        primaryjoin="DebateTopic.id == DebateLog.topic_id"
    )
    summary = relationship('DebateSummary', back_populates='topic', uselist=False)

class Argument(db):
    __tablename__ = 'argument'

    id = Column(Integer, primary_key=True)
    topic_id = Column(Integer, ForeignKey('debate_topic.id'), nullable=False)
    content = Column(Text, nullable=False)
    submission_timestamp = Column(db.DateTime, default=datetime.utcnow)
    status = Column(String(20), default='pending_review')  # 'approved', 'needs_revision', 'rejected'
    ai_feedback_to_user = Column(Text, nullable=True)

class DebateLog(db):
    __tablename__ = 'debate_logs'

    id = Column(Integer, primary_key=True)
    topic_id = Column(Integer, ForeignKey('debate_topic.id'), nullable=False)  # Corrected table name
    round_number = Column(Integer, nullable=False)
    alpha_argument = Column(Text, nullable=False)
    beta_argument = Column(Text, nullable=False)
    moderator_notes = Column(Text, nullable=True)

    topic = relationship('DebateTopic', back_populates='logs')

class DebateSummary(db):
    __tablename__ = 'debate_summaries'

    id = Column(Integer, primary_key=True)
    topic_id = Column(Integer, ForeignKey('debate_topic.id'), nullable=False)  # Corrected table name
    summary = Column(Text, nullable=False)

    topic = relationship('DebateTopic', back_populates='summary')
