"""
send_email.py
Reads newsletter_output.html and sends it as an HTML email
using SMTP credentials stored in GitHub Secrets.
"""

import os
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
from email import encoders
from pathlib import Path

# ---------------------------------------------------------------------------
# Config from environment / secrets
# ---------------------------------------------------------------------------
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ["SMTP_USER"]
SMTP_PASS = os.environ["SMTP_PASS"]
TO_EMAIL  = os.environ.get("TO_EMAIL", "Sagarmurali2004@gmail.com")
CURRENT_DAY = int(os.environ.get("CURRENT_DAY", "1"))
INPUT_FILE = "newsletter_output.html"
PDF_FILE = "newsletter_output.pdf"
REQUIRED_SECTION_MARKERS = {
    "backend": "<!-- SECTION:BACKEND_COMPLETE -->",
    "ai": "<!-- SECTION:AI_COMPLETE -->",
    "sysdesign": "<!-- SECTION:SYSDESIGN_COMPLETE -->",
}


def validate_newsletter(html_body: str) -> None:
    missing = [
        label
        for label, marker in REQUIRED_SECTION_MARKERS.items()
        if marker not in html_body
    ]
    if missing:
        print(
            "[email] ERROR: newsletter_output.html is incomplete. "
            f"Missing section(s): {', '.join(missing)}"
        )
        sys.exit(1)

# ---------------------------------------------------------------------------
# Build the email
# ---------------------------------------------------------------------------
def attach_file(msg: MIMEMultipart, path: Path, filename: str) -> None:
    payload = path.read_bytes()
    attachment = MIMEApplication(payload, _subtype=path.suffix.lstrip(".") or "octet-stream")
    attachment.add_header("Content-Disposition", "attachment", filename=filename)
    msg.attach(attachment)


def build_message(html_body: str, pdf_path: Path) -> MIMEMultipart:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🚀 60-Day Bootcamp — Day {CURRENT_DAY}/60 | Backend + Agentic AI + System Design"
    msg["From"]    = f"Bootcamp Newsletter <{SMTP_USER}>"
    msg["To"]      = TO_EMAIL

    # Plain-text fallback
    plain_text = (
        f"Day {CURRENT_DAY}/60 — 60-Day Backend + Agentic AI + System Design Bootcamp\n\n"
        "Your HTML email client is required to view this newsletter.\n"
        "Please open this email in a client that supports HTML.\n\n"
        "Topics today include Backend Engineering, Agentic AI, System Design, "
        "Industry Pulse, Coding Challenges, and more."
    )

    part1 = MIMEText(plain_text, "plain", "utf-8")
    part2 = MIMEText(html_body, "html", "utf-8")

    # Attach plain first, HTML last (preferred by email clients)
    msg.attach(part1)
    msg.attach(part2)

    attach_file(msg, pdf_path, f"bootcamp_day_{CURRENT_DAY:02d}.pdf")

    # Also attach the HTML file so the reader can open it in a browser
    attachment = MIMEBase("text", "html")
    attachment.set_payload(html_body.encode("utf-8"))
    encoders.encode_base64(attachment)
    attachment.add_header(
        "Content-Disposition",
        "attachment",
        filename=f"bootcamp_day_{CURRENT_DAY:02d}.html",
    )
    msg.attach(attachment)

    return msg


# ---------------------------------------------------------------------------
# Send via SMTP
# ---------------------------------------------------------------------------
def send_email(msg: MIMEMultipart) -> None:
    print(f"[email] Connecting to {SMTP_HOST}:{SMTP_PORT}...")
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=60) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        print(f"[email] Logging in as {SMTP_USER}...")
        server.login(SMTP_USER, SMTP_PASS)
        print(f"[email] Sending to {TO_EMAIL}...")
        server.sendmail(SMTP_USER, [TO_EMAIL], msg.as_string())
    print(f"[email] ✅ Newsletter Day {CURRENT_DAY} sent successfully to {TO_EMAIL}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    html_path = Path(INPUT_FILE)
    if not html_path.exists():
        print(f"[email] ERROR: {INPUT_FILE} not found. Did the generation step succeed?")
        sys.exit(1)
    pdf_path = Path(PDF_FILE)
    if not pdf_path.exists():
        print(f"[email] ERROR: {PDF_FILE} not found. Did the PDF generation step succeed?")
        sys.exit(1)

    html_body = html_path.read_text(encoding="utf-8")
    size_kb = len(html_body.encode("utf-8")) / 1024
    print(f"[email] Loaded {INPUT_FILE} ({size_kb:.1f} KB)")
    validate_newsletter(html_body)
    pdf_size_kb = pdf_path.stat().st_size / 1024
    print(f"[email] Loaded {PDF_FILE} ({pdf_size_kb:.1f} KB)")

    # Gmail limits attachments to 25 MB and inline HTML to ~102 KB before clipping.
    # If the newsletter is very large, warn but proceed.
    if size_kb > 90:
        print(
            f"[email] ⚠️  HTML body is {size_kb:.1f} KB — Gmail may clip the message. "
            "The full newsletter is still attached as an HTML file."
        )

    msg = build_message(html_body, pdf_path)
    send_email(msg)


if __name__ == "__main__":
    main()
