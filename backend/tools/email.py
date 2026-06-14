"""
backend/tools/email.py
Tool to send the finalized cold outreach draft to the user's email.
"""
from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from backend.core.config import settings

logger = logging.getLogger(__name__)

async def send_outreach_email(company_name: str, role_title: str, body: str) -> bool:
    """
    Sends the outreach email draft to the configured SMTP_USER.
    This acts as a 'send to self' feature so the user receives the draft
    in their inbox, ready to be forwarded or copied to the actual hiring manager.
    """
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning("SMTP credentials not configured. Skipping email dispatch.")
        return False

    subject = f"Draft Outreach: {role_title} at {company_name}"
    
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_USER
    msg["To"] = settings.SMTP_USER  # Send to self for review

    try:
        # Use synchronous smtplib in a quick blocking call
        # (For production, consider aiosmtplib, but smtplib is fine for this scale)
        logger.info("Connecting to SMTP server %s:%d", settings.SMTP_HOST, settings.SMTP_PORT)
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
            logger.info("Successfully sent outreach draft email for %s", company_name)
        return True
    except Exception as e:
        logger.error("Failed to send outreach email: %s", e)
        return False
