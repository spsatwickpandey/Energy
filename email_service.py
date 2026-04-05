"""
email_service.py — Gmail SMTP OTP sender
Configure GMAIL_USER and GMAIL_APP_PASSWORD in .env to enable.
Falls back to console print (dev mode) when not configured.

How to get a Gmail App Password:
  1. Go to https://myaccount.google.com/security
  2. Enable 2-Step Verification (if not already on)
  3. Go to https://myaccount.google.com/apppasswords
  4. Type any name (e.g. "Smart Energy") → Generate
  5. Copy the 16-character password → paste in .env (spaces are OK)
"""
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv, find_dotenv

_PLACEHOLDERS = {
    '', 'your_gmail@gmail.com', 'your_gmail_app_password_here',
    'your_16_char_app_password', 'your16charapppassword',
    'xxxxxxxxxxxxxxxxxxxx', 'your_app_password_here'
}


def _load_gmail_creds():
    """Always reload .env so changes take effect without server restart."""
    load_dotenv(find_dotenv(), override=True)
    user = os.getenv('GMAIL_USER', '').strip()
    pwd  = os.getenv('GMAIL_APP_PASSWORD', '').strip().replace(' ', '')
    return user, pwd


def _is_configured(user: str, pwd: str) -> bool:
    return (
        bool(user) and
        user not in _PLACEHOLDERS and
        '@' in user and
        bool(pwd) and
        pwd not in _PLACEHOLDERS and
        len(pwd) >= 16  # 16 chars after stripping spaces
    )


def _build_html(name: str, otp: str) -> str:
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#050A14;font-family:Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0"
         style="background:#050A14;padding:30px 0;">
    <tr><td align="center">
      <table width="520" cellpadding="0" cellspacing="0"
             style="background:linear-gradient(135deg,#0D1B2A,#1a2840);
                    border-radius:16px;overflow:hidden;
                    border:1px solid rgba(255,214,0,0.3);">
        <tr>
          <td style="background:linear-gradient(135deg,#FFD600,#FFA600);
                     padding:28px;text-align:center;">
            <span style="font-size:32px;">⚡</span>
            <h1 style="color:#050A14;margin:8px 0 0;font-size:22px;
                        font-weight:900;font-family:Arial,sans-serif;">
              Smart Energy Optimizer
            </h1>
          </td>
        </tr>
        <tr>
          <td style="padding:36px 40px;">
            <h2 style="color:#FFD600;margin:0 0 14px;font-size:20px;
                        font-family:Arial,sans-serif;">
              Hello, {name}! 👋
            </h2>
            <p style="color:#B0BEC5;font-size:15px;margin:0 0 26px;
                       line-height:1.65;font-family:Arial,sans-serif;">
              Your one-time verification code is below.<br>
              It expires in
              <strong style="color:#FFD600;">10 minutes</strong>.
            </p>
            <div style="background:rgba(255,214,0,0.08);
                        border:2px solid #FFD600;border-radius:14px;
                        padding:30px;text-align:center;margin:0 0 28px;">
              <span style="font-size:52px;font-weight:900;color:#FFD600;
                            letter-spacing:18px;font-family:monospace;">
                {otp}
              </span>
            </div>
            <p style="color:#546E7A;font-size:13px;margin:0;
                       font-family:Arial,sans-serif;">
              If you didn't request this, you can safely ignore this email.
            </p>
          </td>
        </tr>
        <tr>
          <td style="background:rgba(0,0,0,0.35);padding:16px 40px;
                     text-align:center;
                     border-top:1px solid rgba(255,214,0,0.15);">
            <p style="color:#546E7A;font-size:12px;margin:0;
                       font-family:Arial,sans-serif;">
              © 2024 Smart Energy Optimizer · All rights reserved
            </p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""


def send_otp_email(to_email: str, otp: str, name: str):
    """
    Send OTP via Gmail SMTP.
    Reads credentials fresh from .env on every call — no server restart needed.
    Falls back to console print (dev mode) when credentials are not set.
    """
    user, pwd = _load_gmail_creds()

    if _is_configured(user, pwd):
        _send_gmail(to_email, otp, name, user, pwd)
        return

    # ── DEV FALLBACK ──────────────────────────────────────────────────────────
    print(f"\n{'='*57}")
    print(f"  [DEV MODE] OTP for {name} ({to_email}): {otp}")
    print(f"  Gmail not configured — update GMAIL_USER + GMAIL_APP_PASSWORD in .env")
    print(f"{'='*57}\n")


def _send_gmail(to_email: str, otp: str, name: str, user: str, pwd: str):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Your Verification Code — Smart Energy Optimizer"
    msg['From']    = f"Smart Energy Optimizer <{user}>"
    msg['To']      = to_email
    msg.attach(MIMEText(_build_html(name, otp), 'html'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587, timeout=20) as server:
            server.ehlo()
            server.starttls()
            server.login(user, pwd)
            server.sendmail(user, to_email, msg.as_string())
        print(f"[email] ✓ OTP sent via Gmail → {to_email}")
    except smtplib.SMTPAuthenticationError:
        raise RuntimeError(
            "Gmail authentication failed. "
            "Make sure GMAIL_APP_PASSWORD is a 16-character App Password "
            "(NOT your regular Gmail password). "
            "Generate one at: https://myaccount.google.com/apppasswords"
        )
    except smtplib.SMTPException as e:
        raise RuntimeError(f"Gmail SMTP error: {e}")
