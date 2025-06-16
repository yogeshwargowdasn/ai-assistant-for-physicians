# models/prediction_result.py :
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from app import db

class PredictionResult(db.Model):
    __tablename__ = 'prediction_results'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # link with logged-in user
    symptoms = db.Column(db.Text, nullable=False)
    disease = db.Column(db.String(100), nullable=True)
    tests = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


