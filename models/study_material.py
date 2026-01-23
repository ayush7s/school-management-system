from datetime import datetime
from models import db

class StudyMaterial(db.Model):
    __tablename__ = "study_material"   # ← IMPORTANT: explicit table name

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    class_name = db.Column(db.String(50), nullable=False)
    file_name = db.Column(db.String(300), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
