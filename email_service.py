"""
email_service.py — Brevo API OTP sender
Configure BREVO_API_KEY in .env to enable.
Falls back to console print (dev mode) when not configured.
"""
import os
import requests
from dotenv import load_dotenv, find_dotenv

_PLACEHOLDERS = {
    '', 'your_brevo_api_key_here'
}

def _load_brevo_creds():
    """Always reload .env so changes take effect without server restart."""
    load_dotenv(find_dotenv(), override=True)
    return os.getenv('BREVO_API_KEY', '').strip()

def _is_configured(api_key: str) -> bool:
    return bool(api_key) and api_key not in _PLACEHOLDERS

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
    Send OTP via Brevo API.
    Reads credentials fresh from .env on every call — no server restart needed.
    Falls back to console print (dev mode) when credentials are not set.
    """
    api_key = _load_brevo_creds()

    if _is_configured(api_key):
        _send_brevo(to_email, otp, name, api_key)
        return

    # ── DEV FALLBACK ──────────────────────────────────────────────────────────
    print(f"\n{'='*57}")
    print(f"  [DEV MODE] OTP for {name} ({to_email}): {otp}")
    print(f"  Brevo not configured — update BREVO_API_KEY in .env")
    print(f"{'='*57}\n")


def _send_brevo(to_email: str, otp: str, name: str, api_key: str):
    url = "https://api.brevo.com/v3/smtp/email"

    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json"
    }

    payload = {
        "sender": {
            "name": "Smart Energy Optimizer",
            "email": "satwickpandey788@gmail.com"
        },
        "to": [
            {
                "email": to_email,
                "name": name
            }
        ],
        "subject": "Your Verification Code — Smart Energy Optimizer",
        "htmlContent": _build_html(name, otp)
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        print(f"[email] ✓ OTP sent via Brevo → {to_email}")
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        if e.response is not None:
            error_msg += f" Response: {e.response.text}"
        raise RuntimeError(
            f"Brevo API error: {error_msg}\n"
            "Make sure your BREVO_API_KEY is correct."
        )
