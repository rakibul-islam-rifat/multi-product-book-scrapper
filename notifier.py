import logging
import os
import smtplib
import socket
import time
from email.message import EmailMessage

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def load_keys() -> tuple[str, str]:
    load_dotenv()

    Email: str | None = os.getenv("EMAIL")
    password: str | None = os.getenv("APP_PASSWORD")

    if not Email or not password:
        logger.error("No valid Email or Password detected!")
        raise ValueError("No valid Email or Password detected!")

    return Email, password


def build_message(sub, From, To, plain, html_text) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = sub
    msg["From"] = From
    msg["To"] = To
    msg.set_content(plain)
    msg.add_alternative(html_text, subtype="html")
    return msg


def connect_server(Email, password, msg, max_attempts: int = 3) -> None:
    last_error = None

    for attempt in range(1, max_attempts + 1):
        try:
            with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as server:
                server.ehlo()
                server.starttls()
                server.login(Email, password)
                server.send_message(msg)

            logger.info("Email Sent Successfully")
            return

        except smtplib.SMTPAuthenticationError:
            logger.error("Login failed — check email and app password")
            raise

        except smtplib.SMTPRecipientsRefused as e:
            logger.error("Bad recipient address: %s", e.recipients)
            raise ValueError(f"Bad recipient address: {e.recipients}") from e

        except (smtplib.SMTPException, TimeoutError, socket.gaierror) as e:
            last_error = e
            logger.warning("Attempt - %d failed: %s", attempt, e)
            time.sleep(5)

    logger.warning("All %d attempts failed. Last error: %s", max_attempts, last_error)
    raise RuntimeError(f"All {max_attempts} attempts failed. Last error: {last_error}")


def send_alert(sub, plain, html_text):
    Email, password = load_keys()

    msg = build_message(sub, From=Email, To=Email, plain=plain, html_text=html_text)

    connect_server(Email, password, msg)
