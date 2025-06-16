# from app import db
# from datetime import datetime

# class MedicalReport(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     filename = db.Column(db.String(255), nullable=False)
#     upload_date = db.Column(db.DateTime, default=datetime.utcnow)


from app import db
from datetime import datetime

class MedicalReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
