from flask import Blueprint, request, jsonify, session, redirect
from database import get_db
from email_service import send_otp_email
from datetime import datetime, timedelta
from bson import ObjectId
import bcrypt
import random

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/signup', methods=['POST'])
def signup():
    data     = request.get_json() or {}
    name     = data.get('name', '').strip()
    email    = data.get('email', '').strip().lower()
    password = data.get('password', '')

    # ── Validation ────────────────────────────────────────────────────────────
    if not name or not email or not password:
        return jsonify({'success': False, 'error': 'All fields are required.'})
    if '@' not in email or '.' not in email:
        return jsonify({'success': False, 'error': 'Please enter a valid email address.'})
    if len(password) < 8:
        return jsonify({'success': False, 'error': 'Password must be at least 8 characters.'})

    db       = get_db()
    existing = db.users.find_one({'email': email})

    # Block only if already fully verified
    if existing and existing.get('is_verified'):
        return jsonify({'success': False, 'error': 'Email already registered. Please sign in.'})

    # Generate fresh OTP (works for new users AND unverified re-attempts)
    otp           = str(random.randint(100000, 999999))
    otp_expires   = datetime.utcnow() + timedelta(minutes=10)
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    db.users.update_one(
        {'email': email},
        {'$set': {
            'name':          name,
            'email':         email,
            'password_hash': password_hash,
            'is_verified':   False,
            'otp':           otp,
            'otp_expires_at':otp_expires,
            'created_at':    datetime.utcnow()
        }},
        upsert=True
    )

    try:
        send_otp_email(email, otp, name)
    except Exception as e:
        # Roll back the DB write so user can retry cleanly
        if not existing:
            db.users.delete_one({'email': email, 'is_verified': False})
        print(f'[auth/signup] Email error for {email}: {e}')
        return jsonify({'success': False, 'error': f'Failed to send OTP email: {str(e)}'})

    return jsonify({'success': True, 'message': 'OTP sent to your email address.'})


@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    data  = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    otp   = data.get('otp', '').strip()

    if not email or not otp:
        return jsonify({'success': False, 'error': 'Email and OTP are required.'})

    db   = get_db()
    user = db.users.find_one({'email': email})

    if not user:
        return jsonify({'success': False, 'error': 'User not found. Please sign up first.'})

    # Already verified — just log them in (idempotent)
    if user.get('is_verified'):
        session['user_id']    = str(user['_id'])
        session['user_email'] = email
        session['user_name']  = user['name']
        return jsonify({'success': True, 'name': user['name']})

    # Check OTP expiry
    otp_expires = user.get('otp_expires_at')
    if otp_expires and datetime.utcnow() > otp_expires:
        return jsonify({'success': False, 'error': 'OTP has expired. Click "Resend OTP" to get a new one.'})

    # Check OTP value
    if str(user.get('otp', '')).strip() != str(otp).strip():
        return jsonify({'success': False, 'error': 'Invalid OTP. Please check and try again.'})

    # Mark verified & log in
    db.users.update_one(
        {'email': email},
        {'$set': {
            'is_verified': True,
            'otp':         None,
            'last_login':  datetime.utcnow()
        }}
    )

    session['user_id']    = str(user['_id'])
    session['user_email'] = email
    session['user_name']  = user['name']

    return jsonify({'success': True, 'name': user['name']})


@auth_bp.route('/signin', methods=['POST'])
def signin():
    data     = request.get_json() or {}
    email    = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'success': False, 'error': 'Email and password are required.'})

    db   = get_db()
    user = db.users.find_one({'email': email})

    if not user:
        return jsonify({'success': False, 'error': 'No account found with this email. Please sign up.'})

    if not user.get('is_verified'):
        return jsonify({
            'success': False,
            'error':   'Email not verified. Please complete sign-up and verify your OTP first.',
            'needs_verification': True
        })

    # Safely handle missing or malformed password hash
    stored_hash = user.get('password_hash', '')
    if not stored_hash:
        return jsonify({'success': False, 'error': 'Account error. Please contact support.'})

    try:
        password_ok = bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
    except Exception:
        return jsonify({'success': False, 'error': 'Account error. Please sign up again.'})

    if not password_ok:
        return jsonify({'success': False, 'error': 'Incorrect password. Please try again.'})

    db.users.update_one({'email': email}, {'$set': {'last_login': datetime.utcnow()}})

    session['user_id']    = str(user['_id'])
    session['user_email'] = email
    session['user_name']  = user['name']

    return jsonify({'success': True, 'name': user['name']})


@auth_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    data  = request.get_json() or {}
    email = data.get('email', '').strip().lower()

    if not email:
        return jsonify({'success': False, 'error': 'Email is required.'})

    db   = get_db()
    user = db.users.find_one({'email': email})

    if not user:
        return jsonify({'success': False, 'error': 'No account found for this email. Please sign up.'})

    if user.get('is_verified'):
        return jsonify({'success': False, 'error': 'Account already verified. Please sign in.'})

    otp         = str(random.randint(100000, 999999))
    otp_expires = datetime.utcnow() + timedelta(minutes=10)
    db.users.update_one(
        {'email': email},
        {'$set': {'otp': otp, 'otp_expires_at': otp_expires}}
    )

    try:
        send_otp_email(email, otp, user['name'])
    except Exception as e:
        print(f'[auth/resend-otp] Email error for {email}: {e}')
        return jsonify({'success': False, 'error': f'Failed to send OTP: {str(e)}'})

    return jsonify({'success': True, 'message': 'New OTP sent successfully.'})


@auth_bp.route('/signout')
def signout():
    session.clear()
    return redirect('/')
