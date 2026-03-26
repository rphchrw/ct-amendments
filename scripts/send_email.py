#!/usr/bin/env python3
"""
Email helper for the CT Amendment Tracker agent.

Usage:
    python3 scripts/send_email.py --subject "..." --body-file /tmp/report.html

Credentials are read from environment variables:
    EMAIL_SENDER   — Gmail address sending the alert
    EMAIL_PASSWORD — Gmail App Password (16-char)
    EMAIL_TO       — Recipient(s), comma-separated
    SMTP_HOST      — defaults to smtp.gmail.com
    SMTP_PORT      — defaults to 587
"""

import argparse
import os
import re
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def parse_args():
    parser = argparse.ArgumentParser(description="Send HTML email for CT Amendment Tracker")
    parser.add_argument("--subject", required=True, help="Email subject line")
    parser.add_argument("--body-file", required=True, help="Path to HTML body file")
    return parser.parse_args()


def load_credentials():
    required = ["EMAIL_SENDER", "EMAIL_PASSWORD", "EMAIL_TO"]
    missing = [v for v in required if not os.environ.get(v)]
    if missing:
        print(f"ERROR: Missing environment variables: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    return {
        "sender":   os.environ["EMAIL_SENDER"],
        "password": os.environ["EMAIL_PASSWORD"],
        "to":       [r.strip() for r in os.environ["EMAIL_TO"].split(",")],
        "host":     os.environ.get("SMTP_HOST", "smtp.gmail.com"),
        "port":     int(os.environ.get("SMTP_PORT", "587")),
    }


def main():
    args = parse_args()
    creds = load_credentials()

    try:
        with open(args.body_file, "r", encoding="utf-8") as f:
            html_body = f.read()
    except FileNotFoundError:
        print(f"ERROR: Body file not found: {args.body_file}", file=sys.stderr)
        sys.exit(1)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = args.subject
    msg["From"] = creds["sender"]
    msg["To"] = ", ".join(creds["to"])

    plain = html_body.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
    plain = re.sub(r"<[^>]+>", "", plain)
    plain = re.sub(r"\n{3,}", "\n\n", plain).strip()

    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(creds["host"], creds["port"]) as server:
            server.ehlo()
            server.starttls()
            server.login(creds["sender"], creds["password"])
            server.sendmail(creds["sender"], creds["to"], msg.as_string())
        print(f"Email sent successfully to: {', '.join(creds['to'])}")
    except smtplib.SMTPAuthenticationError:
        print("ERROR: SMTP authentication failed. Check EMAIL_SENDER and EMAIL_PASSWORD.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to send email: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

