import os
from functools import wraps
from datetime import datetime, timedelta
from utils.qr_generator import generate_upi_qr
from models import Faculty



from flask import (
    Flask, render_template, request,
    redirect, url_for, send_from_directory,
    session, flash
)
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash

from models import db
from models.user import User
from models.notice import Notice
from models.study_material import StudyMaterial
from models.announcement import Announcement
from models.paid_material import PaidMaterial
from models.payment import Payment

from utils.receipt import generate_receipt
from utils.email_service import send_email

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
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "school_secret_key")

db.init_app(app)

# ---------------- CREATE TABLES + ADMIN ----------------
with app.app_context():
    db.create_all()

    admin_email = os.environ.get("ADMIN_EMAIL")
    admin_password = os.environ.get("ADMIN_PASSWORD")

    if admin_email and admin_password:
        admin = User.query.filter_by(email=admin_email).first()
        if not admin:
            admin = User(
                name="Administrator",
                email=admin_email,
                role="admin"
            )
            db.session.add(admin)

        admin.password = generate_password_hash(admin_password)
        db.session.commit()

# ---------------- FILE UPLOAD CONFIG ----------------
NOTICE_FOLDER = os.path.join(BASE_DIR, "uploads", "notices")
STUDY_MATERIAL_FOLDER = os.path.join(BASE_DIR, "uploads", "study_materials")
ANNOUNCEMENT_FOLDER = os.path.join(BASE_DIR, "uploads", "announcements")
PAID_MATERIAL_FOLDER = os.path.join(BASE_DIR, "uploads", "paid_materials")
RECEIPT_FOLDER = os.path.join(BASE_DIR, "uploads", "receipts")
QR_FOLDER = os.path.join(BASE_DIR, "uploads", "qr_codes")
FACULTY_FOLDER = os.path.join(BASE_DIR, "static", "faculty")


app.config["FACULTY_FOLDER"] = FACULTY_FOLDER

for folder in [
    NOTICE_FOLDER,
    STUDY_MATERIAL_FOLDER,
    ANNOUNCEMENT_FOLDER,
    PAID_MATERIAL_FOLDER,
    RECEIPT_FOLDER,
    QR_FOLDER,
    FACULTY_FOLDER 
]:
    os.makedirs(folder, exist_ok=True)
app.config["QR_FOLDER"] = QR_FOLDER

app.config.update({
    "NOTICE_FOLDER": NOTICE_FOLDER,
    "STUDY_MATERIAL_FOLDER": STUDY_MATERIAL_FOLDER,
    "ANNOUNCEMENT_FOLDER": ANNOUNCEMENT_FOLDER,
    "PAID_MATERIAL_FOLDER": PAID_MATERIAL_FOLDER,
    "RECEIPT_FOLDER": RECEIPT_FOLDER
})

# ---------------- ADMIN DECORATOR ----------------
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("role") != "admin":
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# ---------------- AUTH ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

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
#---------------faculty public--------
@app.route("/faculty")
def faculty_public():
    faculty_members = Faculty.query.filter_by(is_active=True).all()
    return render_template(
        "faculty.html",
        faculty_members=faculty_members
    )

# ---------------- CONTACT ----------------
@app.route("/contact")
def contact():
    return render_template("contact.html")

# ---------------- ADMIN DASHBOARD ----------------
@app.route("/admin")
@admin_required
def admin_dashboard():
    return render_template(
        "admin_dashboard.html",
        notice_count=Notice.query.count(),
        announcement_count=Announcement.query.count(),
        material_count=StudyMaterial.query.count(),
        paid_material_count=PaidMaterial.query.count()
    )

# ---------------- ADMIN PAYMENT HISTORY ----------------
@app.route("/admin/payments")
@admin_required
def admin_payments():
    payments = db.session.query(
        Payment,
        PaidMaterial
    ).join(
        PaidMaterial,
        Payment.material_id == PaidMaterial.id
    ).order_by(
        Payment.created_at.desc()
    ).all()

    return render_template(
        "admin_payments.html",
        payments=payments
    )

# ---------------- NOTICES ----------------
@app.route("/notices", methods=["GET", "POST"])
def notices():
    if request.method == "POST":
        if session.get("role") != "admin":
            return redirect(url_for("login"))

        pdf = request.files.get("pdf")
        filename = None

        if pdf and pdf.filename:
            filename = secure_filename(pdf.filename)
            pdf.save(os.path.join(app.config["NOTICE_FOLDER"], filename))

        db.session.add(
            Notice(
                title=request.form["title"],
                content=request.form["content"],
                pdf_file=filename
            )
        )
        db.session.commit()
        return redirect(url_for("notices"))

    return render_template(
        "notices.html",
        notices=Notice.query.order_by(Notice.created_at.desc()).all()
    )
# ---------------- DOWNLOAD NOTICE PDF ----------------
@app.route("/notices/pdf/<filename>")
def download_notice_pdf(filename):
    return send_from_directory(
        app.config["NOTICE_FOLDER"],
        filename,
        as_attachment=True
    )
# ---------------- DELETE NOTICE ----------------
@app.route("/admin/notices/delete/<int:id>")
@admin_required
def delete_notice(id):
    notice = Notice.query.get_or_404(id)

    # delete PDF file if exists
    if notice.pdf_file:
        pdf_path = os.path.join(app.config["NOTICE_FOLDER"], notice.pdf_file)
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    db.session.delete(notice)
    db.session.commit()

    flash("Notice deleted successfully")
    return redirect(url_for("notices"))


# ---------------- ANNOUNCEMENTS ----------------
@app.route("/announcements", methods=["GET", "POST"])
def announcements():
    if request.method == "POST":
        if session.get("role") != "admin":
            return redirect(url_for("login"))

        file = request.files.get("file")
        filename = None

        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["ANNOUNCEMENT_FOLDER"], filename))

        db.session.add(
            Announcement(
                title=request.form["title"],
                content=request.form["content"],
                file_name=filename
            )
        )
        db.session.commit()
        return redirect(url_for("announcements"))

    return render_template(
        "announcements.html",
        announcements=Announcement.query.order_by(
            Announcement.created_at.desc()
        ).all()
    )
# ---------------- DELETE ANNOUNCEMENT ----------------
@app.route("/admin/announcement/delete/<int:id>")
@admin_required
def delete_announcement(id):
    announcement = Announcement.query.get_or_404(id)

    # delete attached file if exists
    if announcement.file_name:
        file_path = os.path.join(
            app.config["ANNOUNCEMENT_FOLDER"],
            announcement.file_name
        )
        if os.path.exists(file_path):
            os.remove(file_path)

    db.session.delete(announcement)
    db.session.commit()

    flash("Announcement deleted successfully")
    return redirect(url_for("announcements"))

# ---------------- STUDY MATERIALS ----------------
@app.route("/materials", methods=["GET", "POST"])
def materials():
    if request.method == "POST":
        if session.get("role") != "admin":
            return redirect(url_for("login"))

        file = request.files.get("file")
        if not file or not file.filename:
            return redirect(url_for("materials"))

        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["STUDY_MATERIAL_FOLDER"], filename))

        db.session.add(
            StudyMaterial(
                title=request.form["title"],
                subject=request.form["subject"],
                class_name=request.form["class_name"],
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
# ---------------- DOWNLOAD STUDY MATERIAL ----------------
@app.route("/study-material/<filename>")
def download_study_material(filename):
    return send_from_directory(
        app.config["STUDY_MATERIAL_FOLDER"],
        filename,
        as_attachment=True
    )
# ---------------- DELETE STUDY MATERIAL ----------------
@app.route("/admin/material/delete/<int:id>")
@admin_required
def delete_material(id):
    material = StudyMaterial.query.get_or_404(id)

    file_path = os.path.join(
        app.config["STUDY_MATERIAL_FOLDER"],
        material.file_name
    )

    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(material)
    db.session.commit()

    flash("Study material deleted successfully")
    return redirect(url_for("materials"))



# ---------------- ADMIN PAID MATERIALS ----------------
@app.route("/admin/paid-materials", methods=["GET", "POST"])
@admin_required
def admin_paid_materials():
    if request.method == "POST":
        file = request.files.get("file")
        if not file or not file.filename:
            flash("PDF file is required")
            return redirect(url_for("admin_paid_materials"))

        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["PAID_MATERIAL_FOLDER"], filename))

        db.session.add(
            PaidMaterial(
                title=request.form["title"],
                class_name=request.form["class_name"],
                subject=request.form["subject"],
                price=float(request.form["price"]),
                file_name=filename
            )
        )
        db.session.commit()

        flash("Paid material uploaded successfully")
        return redirect(url_for("admin_paid_materials"))

    return render_template(
        "admin_paid_materials.html",
        materials=PaidMaterial.query.order_by(
            PaidMaterial.created_at.desc()
        ).all()
    )

# ---------------- DELETE PAID MATERIAL ----------------
@app.route("/admin/paid-material/delete/<int:id>")
@admin_required
def delete_paid_material(id):
    material = PaidMaterial.query.get_or_404(id)

    file_path = os.path.join(
        app.config["PAID_MATERIAL_FOLDER"],
        material.file_name
    )
    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(material)
    db.session.commit()

    flash("Paid material deleted successfully")
    return redirect(url_for("admin_paid_materials"))
#----------------faculty list----------------
@app.route("/admin/faculty", methods=["GET", "POST"])
@admin_required
def admin_faculty():
    if request.method == "POST":
        name = request.form["name"]
        designation = request.form["designation"]
        photo = request.files["photo"]

        filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config["FACULTY_FOLDER"], filename))

        faculty = Faculty(
            name=name,
            designation=designation,
            image=filename
        )
        db.session.add(faculty)
        db.session.commit()

        flash("Faculty added successfully")
        return redirect(url_for("admin_faculty"))

    faculty_members = Faculty.query.order_by(Faculty.created_at.desc()).all()
    return render_template(
        "admin_faculty.html",
        faculty_members=faculty_members
    )

#-------delete faculty------------------
@app.route("/admin/faculty/delete/<int:id>")
@admin_required
def delete_faculty(id):
    faculty = Faculty.query.get_or_404(id)

    image_path = os.path.join(app.config["FACULTY_FOLDER"], faculty.image)
    if os.path.exists(image_path):
        os.remove(image_path)

    db.session.delete(faculty)
    db.session.commit()

    flash("Faculty deleted")
    return redirect(url_for("admin_faculty"))


# ---------------- PUBLIC PAID MATERIALS ----------------
@app.route("/paid-materials")
def paid_materials():
    selected_class = request.args.get("class")
    selected_subject = request.args.get("subject")

    query = PaidMaterial.query.filter_by(is_active=True)

    if selected_class:
        query = query.filter_by(class_name=selected_class)
    if selected_subject:
        query = query.filter_by(subject=selected_subject)

    materials = query.all()

    classes = [c[0] for c in db.session.query(PaidMaterial.class_name).distinct()]
    subjects = [s[0] for s in db.session.query(PaidMaterial.subject).distinct()]

    return render_template(
        "paid_materials.html",
        paid_materials=materials,
        classes=classes,
        subjects=subjects,
        selected_class=selected_class,
        selected_subject=selected_subject
    )

# ---------------- START PAYMENT ----------------
@app.route("/start-payment", methods=["POST"])
def start_payment():
    material_id = request.form.get("material_id")
    email = request.form.get("email")

    if not material_id or not email:
        flash("Invalid request")
        return redirect(url_for("paid_materials"))

    if not email.endswith("@gmail.com"):
        flash("Please enter a valid Gmail address")
        return redirect(url_for("paid_materials"))

    material = PaidMaterial.query.filter_by(
        id=material_id,
        is_active=True
    ).first()

    if not material:
        flash("Material not found")
        return redirect(url_for("paid_materials"))

    session["payment_material_id"] = material.id
    session["payment_email"] = email
    session["payment_amount"] = material.price

    return redirect(url_for("payment_page"))

# ---------------- PAYMENT PAGE ----------------
@app.route("/payment")
def payment_page():
    material_id = session.get("payment_material_id")
    email = session.get("payment_email")

    if not material_id:
        return redirect(url_for("paid_materials"))

    material = PaidMaterial.query.get_or_404(material_id)

    upi_id = os.environ.get("UPI_ID")
    upi_name = os.environ.get("UPI_NAME")

    upi_link = (
        f"upi://pay?"
        f"pa={upi_id}"
        f"&pn={upi_name.replace(' ', '%20')}"
        f"&am={material.price}"
        f"&cu=INR"
        f"&tn=Paid%20Study%20Material"
    )

    # ---------- QR GENERATION ----------
    qr_filename = f"upi_qr_{material.id}_{material.price}.png"
    qr_path = os.path.join(app.config["QR_FOLDER"], qr_filename)

    if not os.path.exists(qr_path):
        generate_upi_qr(upi_link, qr_path)

    return render_template(
        "payment.html",
        material=material,
        amount=material.price,
        email=email,
        upi_id=upi_id,
        upi_name=upi_name,
        upi_link=upi_link,
        qr_image=qr_filename   # ✅ now defined
    )

# ---------------- SUBMIT PAYMENT ----------------
@app.route("/submit-payment", methods=["POST"])
def submit_payment():
    email = request.form.get("email")
    material_id = request.form.get("material_id")
    utr = request.form.get("utr")

    # -------- BASIC VALIDATION --------
    if not email or not material_id or not utr:
        flash("Invalid submission.")
        return redirect(url_for("paid_materials"))

    if len(utr.strip()) < 8:
        flash("Invalid UTR / Transaction ID.")
        return redirect(url_for("paid_materials"))

    # -------- 🚨 BLOCK REUSED UTR (GLOBAL) --------
    existing_utr = Payment.query.filter_by(utr=utr.strip()).first()
    if existing_utr:
        flash("This UTR / Transaction ID has already been used.")
        return redirect(url_for("paid_materials"))

    material = PaidMaterial.query.get_or_404(material_id)

    # -------- RATE LIMIT (24 HOURS / SAME MATERIAL) --------
    last_payment = Payment.query.filter_by(
        email=email,
        material_id=material.id
    ).order_by(Payment.created_at.desc()).first()

    if last_payment and datetime.utcnow() - last_payment.created_at < timedelta(hours=24):
        flash("You already purchased this material in the last 24 hours.")
        return redirect(url_for("paid_materials"))

    # -------- SAVE PAYMENT --------
    payment = Payment(
        material_id=material.id,
        email=email,
        amount=material.price,
        utr=utr.strip()
    )
    db.session.add(payment)
    db.session.commit()

    # -------- RECEIPT --------
    receipt_path = os.path.join(
        app.config["RECEIPT_FOLDER"],
        f"receipt_{payment.id}.pdf"
    )

    generate_receipt(
        receipt_path=receipt_path,
        school_name=os.environ.get("SCHOOL_NAME", "School"),
        email=email,
        material=material,
        amount=material.price,
        utr=utr.strip()
    )

    # -------- EMAIL --------
    download_link = url_for(
        "download_paid_material",
        token=payment.download_token,
        _external=True
    )

    send_email(
        to_email=email,
        subject="Your Study Material & Receipt",
        body=f"""
Thank you for your payment.

Download your study material here:
{download_link}

This link is valid for 24 hours.
""",
        attachments=[receipt_path]
    )

    flash("Payment successful! PDF and receipt sent to your Gmail.")
    return redirect(url_for("home"))


# ---------------- DOWNLOAD PAID MATERIAL ----------------
@app.route("/download/<token>")
def download_paid_material(token):
    payment = Payment.query.filter_by(download_token=token).first_or_404()

    if datetime.utcnow() - payment.created_at > timedelta(hours=24):
        flash("Download link expired.")
        return redirect(url_for("home"))

    material = PaidMaterial.query.get(payment.material_id)

    return send_from_directory(
        app.config["PAID_MATERIAL_FOLDER"],
        material.file_name,
        as_attachment=True
    )
# ---------------- SERVE UPI QR IMAGE ----------------
@app.route("/upi-qr/<filename>")
def download_qr(filename):
    return send_from_directory(
        app.config["QR_FOLDER"],
        filename
    )


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")

