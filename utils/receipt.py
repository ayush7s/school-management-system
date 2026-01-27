from datetime import datetime
import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas


def _draw_watermark(c: canvas.Canvas, width: float, height: float) -> None:
    """Draw a subtle repeated diagonal watermark 'FSBA' across the page."""
    c.saveState()
    c.setFillColor(colors.Color(0, 0, 0, alpha=0.045))
    c.setFont("Helvetica-Bold", 18)

    # Rotate around center and tile
    c.translate(width / 2, height / 2)
    c.rotate(35)

    step_x = 6.5 * cm
    step_y = 4.5 * cm
    for x in range(-8, 9):
        for y in range(-10, 11):
            c.drawString(x * step_x, y * step_y, "FSBA")

    c.restoreState()


def generate_receipt(receipt_path, school_name, email, material, amount, utr):
    c = canvas.Canvas(receipt_path, pagesize=A4)
    width, height = A4

    # Watermark (behind everything)
    _draw_watermark(c, width, height)

    # Colors
    GREEN = colors.HexColor("#0b6e3f")
    LIGHT_GREEN = colors.HexColor("#e8f5e9")
    DARK = colors.HexColor("#1f2933")
    MUTED = colors.HexColor("#6b7280")

    # Layout constants
    margin_x = 2.0 * cm
    top_y = height - 2.2 * cm
    content_w = width - 2 * margin_x

    # Header card
    header_h = 3.2 * cm
    c.setFillColor(LIGHT_GREEN)
    c.setStrokeColor(colors.HexColor("#c1e3c8"))
    c.roundRect(margin_x, top_y - header_h, content_w, header_h, 12, stroke=1, fill=1)

    # Logo (keep path as-is; fallback if missing)
    logo_path = "static/images/logo.jpeg"
    if os.path.exists(logo_path):
        c.drawImage(logo_path, margin_x + 0.6 * cm, top_y - header_h + 0.45 * cm, width=2.2 * cm, height=2.2 * cm, mask="auto")

    c.setFillColor(GREEN)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin_x + 3.2 * cm, top_y - 1.2 * cm, school_name)

    c.setFillColor(DARK)
    c.setFont("Helvetica", 10)
    c.drawString(margin_x + 3.2 * cm, top_y - 2.0 * cm, "Payment Receipt / Invoice")

    # Invoice meta
    invoice_no = f"INV-{datetime.now().strftime('%Y%m%d')}-{str(utr)[-6:]}"
    invoice_date = datetime.now().strftime("%d-%m-%Y %H:%M")

    c.setFillColor(MUTED)
    c.setFont("Helvetica", 9)
    c.drawRightString(margin_x + content_w - 0.6 * cm, top_y - 1.1 * cm, f"Invoice No: {invoice_no}")
    c.drawRightString(margin_x + content_w - 0.6 * cm, top_y - 1.7 * cm, f"Date: {invoice_date}")

    # Bill-to block
    y = top_y - header_h - 1.0 * cm
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin_x, y, "Bill To")
    y -= 0.55 * cm

    c.setFont("Helvetica", 10)
    c.setFillColor(DARK)
    c.drawString(margin_x, y, email)
    y -= 0.9 * cm

    # Items table
    table_top = y
    row_h = 0.9 * cm
    col_item = margin_x
    col_price = margin_x + content_w - 4.2 * cm
    col_total = margin_x + content_w - 0.6 * cm

    # Header row
    c.setFillColor(GREEN)
    c.setStrokeColor(GREEN)
    c.roundRect(margin_x, table_top - row_h, content_w, row_h, 8, stroke=1, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(col_item + 0.35 * cm, table_top - 0.62 * cm, "Item")
    c.drawString(col_price, table_top - 0.62 * cm, "Price")
    c.drawRightString(col_total, table_top - 0.62 * cm, "Total")

    # Item row
    table_top -= row_h
    c.setFillColor(colors.white)
    c.setStrokeColor(colors.HexColor("#e2e8f0"))
    c.roundRect(margin_x, table_top - row_h, content_w, row_h, 8, stroke=1, fill=1)
    c.setFillColor(DARK)
    c.setFont("Helvetica", 10)
    c.drawString(col_item + 0.35 * cm, table_top - 0.62 * cm, material.title)
    c.drawString(col_price, table_top - 0.62 * cm, f"₹{amount}")
    c.drawRightString(col_total, table_top - 0.62 * cm, f"₹{amount}")

    # Totals block
    totals_y = table_top - row_h - 1.0 * cm
    c.setFont("Helvetica", 10)
    c.setFillColor(MUTED)
    c.drawRightString(col_total, totals_y, "Subtotal")
    c.setFillColor(DARK)
    c.drawRightString(col_total, totals_y - 0.55 * cm, f"₹{amount}")

    c.setFillColor(MUTED)
    c.drawRightString(col_total, totals_y - 1.2 * cm, "Total Amount")
    c.setFillColor(GREEN)
    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(col_total, totals_y - 1.85 * cm, f"₹{amount}")

    # Payment info card
    info_y = totals_y - 2.8 * cm
    info_h = 2.4 * cm
    c.setFillColor(colors.HexColor("#f5faf6"))
    c.setStrokeColor(colors.HexColor("#e2e8f0"))
    c.roundRect(margin_x, info_y - info_h, content_w, info_h, 12, stroke=1, fill=1)

    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin_x + 0.6 * cm, info_y - 0.7 * cm, "Payment Details")

    c.setFont("Helvetica", 9)
    c.setFillColor(MUTED)
    c.drawString(margin_x + 0.6 * cm, info_y - 1.35 * cm, f"Mode: UPI")
    c.drawString(margin_x + 0.6 * cm, info_y - 1.95 * cm, f"UTR / Transaction ID: {utr}")
    c.drawRightString(margin_x + content_w - 0.6 * cm, info_y - 1.35 * cm, "Status: PAYMENT RECEIVED")

    # Footer note
    footer_y = 1.8 * cm
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 9)
    c.drawCentredString(width / 2, footer_y, "Thank you for your payment. This is a computer-generated invoice; no signature required.")

    c.showPage()
    c.save()
