from pymongo import MongoClient, ASCENDING
from pymongo.errors import OperationFailure, ServerSelectionTimeoutError, ConnectionFailure
import os
import certifi
from dotenv import load_dotenv, find_dotenv

_client = None
_db     = None


def get_db():
    global _client, _db
    if _db is None:
        # Always reload .env so URI changes take effect without restart
        load_dotenv(find_dotenv(), override=True)
        uri = os.getenv('MONGODB_URI', '').strip()
        if not uri:
            raise RuntimeError(
                "MONGODB_URI is not set in .env — "
                "please add your MongoDB Atlas connection string."
            )
        try:
            _client = MongoClient(
                uri,
                tlsCAFile=certifi.where(),
                serverSelectionTimeoutMS=20000,
                connectTimeoutMS=20000,
                socketTimeoutMS=20000,
            )
            # Verify connection is actually alive
            _client.admin.command('ping')
        except ServerSelectionTimeoutError as e:
            _client = None
            _db     = None
            err = str(e)
            if 'TLSV1_ALERT_INTERNAL_ERROR' in err or 'SSL' in err:
                raise RuntimeError(
                    "MongoDB Atlas rejected the connection (SSL/TLS error). "
                    "Your IP address is likely not whitelisted. "
                    "Fix: Go to cloud.mongodb.com → Security → Network Access → "
                    "Add IP Address → Add Current IP Address → Confirm."
                ) from e
            raise RuntimeError(
                f"Cannot reach MongoDB Atlas (timeout). "
                f"Check your MONGODB_URI and network connection. Detail: {err[:200]}"
            ) from e
        except ConnectionFailure as e:
            _client = None
            _db     = None
            raise RuntimeError(f"MongoDB connection failed: {e}") from e

        _db = _client['smart_energy']

        # ── Ensure indexes (idempotent) ──────────────────────────────────────
        try:
            _db.users.create_index(
                [('email', ASCENDING)], unique=True, background=True
            )
            _db.sessions.create_index(
                [('user_id', ASCENDING)], background=True
            )
            _db.sessions.create_index(
                [('created_at', ASCENDING)], background=True
            )
        except OperationFailure as e:
            print(f"[database] Index warning: {e}")

    return _db


def reset_db():
    """Force re-connection on next get_db() call. Useful after fixing connectivity."""
    global _client, _db
    if _client:
        try:
            _client.close()
        except Exception:
            pass
    _client = None
    _db     = None
