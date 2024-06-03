from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class MessageTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)

class ScheduledMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text, nullable=False)
    send_time = db.Column(db.String(5), nullable=False)  # Store time as HH:MM
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

class IncomingMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    analysis_result = db.Column(db.Text, nullable=False)
    date_received = db.Column(db.DateTime, default=datetime.utcnow)

class CustomerInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    clearance_code = db.Column(db.String(20), nullable=False)
    date_received = db.Column(db.DateTime, default=datetime.utcnow)

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    check_interval = db.Column(db.Integer, nullable=False, default=5)  # minutes
    last_checked = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
