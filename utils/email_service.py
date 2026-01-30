import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

load_dotenv(override=True)


def send_email(to_email, subject, body, attachments):
    """
    Sends an email with optional PDF attachments using Gmail SMTP.
    Requires EMAIL_USER and EMAIL_PASS to be set in environment variables.
    """

    email_user = os.environ.get("EMAIL_USER")
    email_pass = os.environ.get("EMAIL_PASS")

    if not email_user or not email_pass:
        raise RuntimeError(
            "EMAIL_USER or EMAIL_PASS is not set in environment variables."
        )

    msg = EmailMessage()
    msg["From"] = email_user
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    # Attach files safely
    for file_path in attachments:
        if not file_path or not os.path.exists(file_path):
            continue  # Skip missing files

        try:
            with open(file_path, "rb") as f:
                file_data = f.read()
                file_name = os.path.basename(file_path)

            msg.add_attachment(
                file_data,
                maintype="application",
                subtype="pdf",
                filename=file_name
            )
        except Exception as e:
            # Do not break email for attachment failure
            print(f"[EMAIL WARNING] Could not attach {file_path}: {e}")

    # Send email
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20) as smtp:
            smtp.login(email_user, email_pass)
            smtp.send_message(msg)
    except Exception as e:
        raise RuntimeError(f"Failed to send email via SMTP: {e}")
