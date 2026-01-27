import uuid
from datetime import datetime
from models import db

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    material_id = db.Column(
        db.Integer,
        db.ForeignKey("paid_materials.id"),
        nullable=False
    )

    email = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    utr = db.Column(db.String(100), nullable=False, unique=True)


    download_token = db.Column(
        db.String(100),
        unique=True,
        nullable=False,
        default=lambda: str(uuid.uuid4())
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
