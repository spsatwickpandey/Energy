"""
wsgi.py — Gunicorn entry point for production deployment.
Usage: gunicorn wsgi:app --workers 2 --timeout 120 --bind 0.0.0.0:$PORT
"""
from app import app

if __name__ == '__main__':
    app.run()