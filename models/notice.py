from datetime import datetime
from models import db

class Notice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    pdf_file = db.Column(db.String(300), nullable=True)  # NEW
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
