from app import db
from datetime import datetime

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    reason = db.Column(db.String(255), nullable=False)

    doctor = db.relationship('User', foreign_keys=[doctor_id], backref='doctor_appointments', lazy=True)
    patient = db.relationship('User', foreign_keys=[patient_id], backref='patient_appointments', lazy=True)
