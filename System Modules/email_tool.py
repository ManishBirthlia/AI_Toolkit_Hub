"""
email_tool.py — Email tools for the Jarvis AI agent.

Provides helpers to send emails via SMTP and read the latest emails
via IMAP.  Credentials are pulled from environment variables.
"""

import os
import email
import smtplib
import imaplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header


# ── Configuration from environment ───────────────────────────────────────────

def _get_email_config() -> dict:
    """Read email configuration from environment variables.

    Expected env vars:
        EMAIL_ADDRESS       — Your email address (e.g. you@gmail.com)
        EMAIL_PASSWORD      — App password (NOT your real password)
        EMAIL_SMTP_SERVER   — SMTP host (default: smtp.gmail.com)
        EMAIL_SMTP_PORT     — SMTP port (default: 587)
        EMAIL_IMAP_SERVER   — IMAP host (default: imap.gmail.com)
    """
    return {
        "address": os.getenv("EMAIL_ADDRESS", ""),
        "password": os.getenv("EMAIL_PASSWORD", ""),
        "smtp_server": os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com"),
        "smtp_port": int(os.getenv("EMAIL_SMTP_PORT", "587")),
        "imap_server": os.getenv("EMAIL_IMAP_SERVER", "imap.gmail.com"),
    }


# ── Public Tool Functions ────────────────────────────────────────────────────

def send_email(to: str, subject: str, body: str, html: bool = False) -> dict:
    """Send an email via SMTP.

    Reads sender address and credentials from environment variables
    (``EMAIL_ADDRESS``, ``EMAIL_PASSWORD``, ``EMAIL_SMTP_SERVER``,
    ``EMAIL_SMTP_PORT``).

    Args:
        to:      Recipient email address.
        subject: Email subject line.
        body:    Email body text.
        html:    If True, send the body as HTML instead of plain text.

    Returns:
        dict confirming delivery.
    """
    cfg = _get_email_config()
    if not cfg["address"] or not cfg["password"]:
        return {
            "success": False,
            "result": None,
            "error": "EMAIL_ADDRESS and EMAIL_PASSWORD must be set in environment variables.",
        }
    try:
        msg = MIMEMultipart()
        msg["From"] = cfg["address"]
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html" if html else "plain"))

        with smtplib.SMTP(cfg["smtp_server"], cfg["smtp_port"]) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(cfg["address"], cfg["password"])
            server.sendmail(cfg["address"], to, msg.as_string())

        return {"success": True, "result": f"Email sent to {to}", "error": None}
    except smtplib.SMTPAuthenticationError:
        return {
            "success": False, "result": None,
            "error": "SMTP authentication failed. Use an App Password for Gmail.",
        }
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def read_latest_emails(count: int = 5, folder: str = "INBOX") -> dict:
    """Read the latest N emails from the mailbox via IMAP.

    Args:
        count:  Number of recent emails to fetch (default 5).
        folder: Mailbox folder to read from (default 'INBOX').

    Returns:
        dict with ``result`` containing a list of email summary dicts,
        each with ``from``, ``subject``, ``date``, and a ``body_snippet``.
    """
    cfg = _get_email_config()
    if not cfg["address"] or not cfg["password"]:
        return {
            "success": False,
            "result": None,
            "error": "EMAIL_ADDRESS and EMAIL_PASSWORD must be set in environment variables.",
        }
    try:
        mail = imaplib.IMAP4_SSL(cfg["imap_server"])
        mail.login(cfg["address"], cfg["password"])
        mail.select(folder, readonly=True)

        # Search for all emails and pick the latest N
        status, data = mail.search(None, "ALL")
        if status != "OK":
            return {"success": False, "result": None, "error": "Failed to search mailbox."}

        email_ids = data[0].split()
        latest_ids = email_ids[-count:] if len(email_ids) >= count else email_ids
        latest_ids.reverse()  # newest first

        emails = []
        for eid in latest_ids:
            status, msg_data = mail.fetch(eid, "(RFC822)")
            if status != "OK":
                continue

            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)

            # Decode subject
            subj_parts = decode_header(msg.get("Subject", ""))
            subject = ""
            for part, enc in subj_parts:
                if isinstance(part, bytes):
                    subject += part.decode(enc or "utf-8", errors="replace")
                else:
                    subject += part

            # Extract body snippet
            body_snippet = ""
            if msg.is_multipart():
                for part in msg.walk():
                    ctype = part.get_content_type()
                    if ctype == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload:
                            body_snippet = payload.decode("utf-8", errors="replace")[:500]
                        break
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    body_snippet = payload.decode("utf-8", errors="replace")[:500]

            emails.append({
                "from": msg.get("From", ""),
                "subject": subject,
                "date": msg.get("Date", ""),
                "body_snippet": body_snippet,
            })

        mail.logout()
        return {"success": True, "result": emails, "error": None}
    except imaplib.IMAP4.error as exc:
        return {"success": False, "result": None, "error": f"IMAP error: {exc}"}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


# ── Anthropic Tool Schema ────────────────────────────────────────────────────

def get_tool_schema() -> list[dict]:
    """Return Anthropic-compatible tool definitions for this module."""
    return [
        {
            "name": "send_email",
            "description": "Send an email via SMTP using preconfigured credentials from environment variables.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "Recipient email address."
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject line."
                    },
                    "body": {
                        "type": "string",
                        "description": "Email body content."
                    },
                    "html": {
                        "type": "boolean",
                        "description": "If true, send body as HTML. Defaults to false (plain text)."
                    }
                },
                "required": ["to", "subject", "body"]
            }
        },
        {
            "name": "read_latest_emails",
            "description": "Read the latest N emails from the inbox via IMAP.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "count": {
                        "type": "integer",
                        "description": "Number of recent emails to fetch. Defaults to 5."
                    },
                    "folder": {
                        "type": "string",
                        "description": "Mailbox folder to read from. Defaults to 'INBOX'."
                    }
                },
                "required": []
            }
        },
    ]
