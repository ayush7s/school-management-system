from app import app
from models import db
from models.notice import Notice
from models.study_material import StudyMaterial
from models.user import User
from models.announcement import Announcement

with app.app_context():
    db.create_all()
    print("Database created successfully")
