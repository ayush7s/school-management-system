import os
from functools import wraps

from flask import (
    Flask, render_template, request,
    redirect, url_for, send_from_directory,
    session, flash
)
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash

from models import db
from models.user import User
from models.notice import Notice
from models.study_material import StudyMaterial
from models.announcement import Announcement

# ---------------- APP INIT ----------------
app = Flask(__name__)

# ---------------- BASE DIRECTORY ----------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# ---------------- DATABASE CONFIG ----------------
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
os.makedirs(INSTANCE_DIR, exist_ok=True)

DB_PATH = os.path.join(INSTANCE_DIR, "school.db")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + DB_PATH
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "school_secret_key"

db.init_app(app)

# ---------------- FILE UPLOAD CONFIG ----------------
NOTICE_FOLDER = os.path.join(BASE_DIR, "uploads", "notices")
STUDY_MATERIAL_FOLDER = os.path.join(BASE_DIR, "uploads", "study_materials")
ANNOUNCEMENT_FOLDER = os.path.join(BASE_DIR, "uploads", "announcements")

os.makedirs(NOTICE_FOLDER, exist_ok=True)
os.makedirs(STUDY_MATERIAL_FOLDER, exist_ok=True)
os.makedirs(ANNOUNCEMENT_FOLDER, exist_ok=True)

app.config["NOTICE_FOLDER"] = NOTICE_FOLDER
app.config["STUDY_MATERIAL_FOLDER"] = STUDY_MATERIAL_FOLDER
app.config["ANNOUNCEMENT_FOLDER"] = ANNOUNCEMENT_FOLDER

# ---------------- ADMIN DECORATOR ----------------
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("role") != "admin":
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# ---------------- ADMIN DASHBOARD ----------------
@app.route("/admin")
@admin_required
def admin_dashboard():
    return render_template(
        "admin_dashboard.html",
        notice_count=Notice.query.count(),
        announcement_count=Announcement.query.count(),
        material_count=StudyMaterial.query.count()
    )

# ---------------- AUTH ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["role"] = user.role
            return redirect(url_for("home"))

        flash("Invalid credentials")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template(
        "index.html",
        notices=Notice.query.order_by(Notice.created_at.desc()).limit(5).all(),
        announcements=Announcement.query.order_by(
            Announcement.created_at.desc()
        ).limit(1).all()
    )

# ---------------- CONTACT ----------------
@app.route("/contact")
def contact():
    return render_template("contact.html")

# ---------------- NOTICES ----------------
@app.route("/notices", methods=["GET", "POST"])
def notices():
    if request.method == "POST":
        if session.get("role") != "admin":
            return redirect(url_for("login"))

        title = request.form["title"]
        content = request.form["content"]

        pdf = request.files.get("pdf")
        filename = None
        if pdf and pdf.filename:
            filename = secure_filename(pdf.filename)
            pdf.save(os.path.join(app.config["NOTICE_FOLDER"], filename))

        db.session.add(Notice(title=title, content=content, pdf_file=filename))
        db.session.commit()
        return redirect(url_for("notices"))

    return render_template(
        "notices.html",
        notices=Notice.query.order_by(Notice.created_at.desc()).all()
    )


@app.route("/notice/delete/<int:id>")
@admin_required
def delete_notice(id):
    notice = Notice.query.get_or_404(id)
    db.session.delete(notice)
    db.session.commit()
    return redirect(url_for("notices"))


@app.route("/notice/<int:notice_id>")
def notice_detail(notice_id):
    return render_template(
        "notice_detail.html",
        notice=Notice.query.get_or_404(notice_id)
    )


@app.route("/uploads/notices/<filename>")
def download_notice_pdf(filename):
    return send_from_directory(
        app.config["NOTICE_FOLDER"], filename, as_attachment=True
    )

# ---------------- ANNOUNCEMENTS ----------------
@app.route("/announcements", methods=["GET", "POST"])
def announcements():
    if request.method == "POST":
        if session.get("role") != "admin":
            return redirect(url_for("login"))

        title = request.form["title"]
        content = request.form["content"]

        file = request.files.get("file")
        filename = None
        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["ANNOUNCEMENT_FOLDER"], filename))

        db.session.add(
            Announcement(title=title, content=content, file_name=filename)
        )
        db.session.commit()
        return redirect(url_for("announcements"))

    return render_template(
        "announcements.html",
        announcements=Announcement.query.order_by(
            Announcement.created_at.desc()
        ).all()
    )


@app.route("/announcement/delete/<int:id>")
@admin_required
def delete_announcement(id):
    ann = Announcement.query.get_or_404(id)
    db.session.delete(ann)
    db.session.commit()
    return redirect(url_for("announcements"))

# ✅ FIX ADDED: ANNOUNCEMENT FILE DOWNLOAD
@app.route("/uploads/announcements/<filename>")
def download_announcement_file(filename):
    return send_from_directory(
        app.config["ANNOUNCEMENT_FOLDER"], filename, as_attachment=True
    )

# ---------------- STUDY MATERIALS ----------------
@app.route("/materials", methods=["GET", "POST"])
def materials():
    if request.method == "POST":
        if session.get("role") != "admin":
            return redirect(url_for("login"))

        title = request.form["title"]
        subject = request.form["subject"]
        class_name = request.form["class_name"]

        file = request.files.get("file")
        if not file or not file.filename:
            return redirect(url_for("materials"))

        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["STUDY_MATERIAL_FOLDER"], filename))

        db.session.add(
            StudyMaterial(
                title=title,
                subject=subject,
                class_name=class_name,
                file_name=filename
            )
        )
        db.session.commit()
        return redirect(url_for("materials"))

    return render_template(
        "materials.html",
        materials=StudyMaterial.query.order_by(
            StudyMaterial.uploaded_at.desc()
        ).all()
    )


@app.route("/material/delete/<int:id>")
@admin_required
def delete_material(id):
    material = StudyMaterial.query.get_or_404(id)
    db.session.delete(material)
    db.session.commit()
    return redirect(url_for("materials"))


@app.route("/uploads/study_materials/<filename>")
def download_study_material(filename):
    return send_from_directory(
        app.config["STUDY_MATERIAL_FOLDER"], filename, as_attachment=True
    )

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
