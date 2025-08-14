
from dataclasses import dataclass
from typing import Literal, Optional
import smtplib
from email.mime.text import MIMEText
from .config import settings

Op = Literal['>=', '<=']

@dataclass
class AlertRule:
    coin_id: str
    coin_symbol: str
    op: Op
    threshold: float
    vs: str = "usd"
    email: bool = False

    def triggered(self, price: float) -> bool:
        return (price >= self.threshold) if self.op == '>=' else (price <= self.threshold)

def send_email(subject: str, body: str) -> Optional[str]:
    if not (settings.smtp_host and settings.smtp_user and settings.smtp_pass and settings.alert_to):
        return "Email settings not configured"
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = settings.smtp_user
    msg['To'] = settings.alert_to
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as s:
            s.starttls()
            s.login(settings.smtp_user, settings.smtp_pass)
            s.send_message(msg)
        return None
    except Exception as e:
        return str(e)
