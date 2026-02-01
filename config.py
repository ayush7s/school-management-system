import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

    DATABASE_URL = os.environ.get("DATABASE_URL")

    if DATABASE_URL:
        # Production (Render / Supabase)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Local development (SQLite)
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(
            BASE_DIR, "instance", "school.db"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
