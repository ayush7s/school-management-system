from datetime import datetime
from models import db

class PaidMaterial(db.Model):
    __tablename__ = "paid_materials"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    class_name = db.Column(db.String(50), nullable=False)     # ✅ NEW
    subject = db.Column(db.String(100), nullable=False)       # ✅ NEW
    description = db.Column(db.Text, nullable=True)

    file_name = db.Column(db.String(255), nullable=False)

    price = db.Column(db.Float, nullable=False)

    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<PaidMaterial {self.title}>"
