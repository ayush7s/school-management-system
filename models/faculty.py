from datetime import datetime
from models import db


class Faculty(db.Model):
    __tablename__ = "faculty"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(120), nullable=False)
    designation = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(120), nullable=True)

    image = db.Column(db.String(255), nullable=False)  # image filename
    description = db.Column(db.Text, nullable=True)

    is_active = db.Column(db.Boolean, default=True)
    
    is_principal = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Faculty {self.name}>"
