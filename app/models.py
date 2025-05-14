from app import db
from datetime import datetime

class DebateTopic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    creation_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    arguments = db.relationship('Argument', backref='topic', lazy=True)

class Argument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('debate_topic.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    submission_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending_review')  # 'approved', 'needs_revision', 'rejected'
    ai_feedback_to_user = db.Column(db.Text, nullable=True)
