import os
import json
import logging
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, auth as firebase_auth_module, exceptions as firebase_exceptions
from django.conf import settings

logger = logging.getLogger(__name__)

# Exported variables
FIREBASE_ADMIN_INITIALIZED = False
auth = None  # will be set to firebase_admin.auth or to a thin wrapper

def _init_from_service_account_path(path: Path):
    cred = credentials.Certificate(str(path))
    app = firebase_admin.initialize_app(cred)
    return firebase_auth_module

def _init_from_service_account_json(json_str: str):
    info = json.loads(json_str)
    cred = credentials.Certificate(info)
    app = firebase_admin.initialize_app(cred)
    return firebase_auth_module

# Try multiple config sources (settings, env, common file locations)
service_account_path = getattr(settings, "FIREBASE_SERVICE_ACCOUNT_PATH", None) or os.environ.get("FIREBASE_SERVICE_ACCOUNT_PATH")
service_account_json = getattr(settings, "FIREBASE_SERVICE_ACCOUNT_JSON", None) or os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON")
google_app_creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", None)

try:
    # If already initialized, reuse the auth module
    if not firebase_admin._apps:
        # 1) explicit path
        if service_account_path:
            path = Path(service_account_path)
            if path.exists():
                auth = _init_from_service_account_path(path)
                FIREBASE_ADMIN_INITIALIZED = True
                logger.info("Initialized Firebase Admin from service account path: %s", path)
            else:
                raise FileNotFoundError(f"Service account file not found at {path}")

        # 2) explicit JSON string
        elif service_account_json:
            auth = _init_from_service_account_json(service_account_json)
            FIREBASE_ADMIN_INITIALIZED = True
            logger.info("Initialized Firebase Admin from JSON string.")

        # 3) GOOGLE_APPLICATION_CREDENTIALS env var (common)
        elif google_app_creds:
            path = Path(google_app_creds)
            if path.exists():
                auth = _init_from_service_account_path(path)
                FIREBASE_ADMIN_INITIALIZED = True
                logger.info("Initialized Firebase Admin from GOOGLE_APPLICATION_CREDENTIALS: %s", path)
            else:
                raise FileNotFoundError(f"GOOGLE_APPLICATION_CREDENTIALS file not found at {path}")

        # 4) try to auto-detect a JSON in Django BASE_DIR / certs (development convenience)
        else:
            base_dir = getattr(settings, "BASE_DIR", None)
            if base_dir:
                certs_dir = Path(base_dir) / "certs"
                if certs_dir.exists() and certs_dir.is_dir():
                    # look for likely json files (e.g. containing 'firebase' or ending with .json)
                    candidates = [p for p in certs_dir.glob("*.json")]
                    candidates = sorted(candidates)  # deterministic pick
                    if candidates:
                        # prefer names containing 'firebase' or 'service' if available
                        preferred = sorted(candidates, key=lambda p: (0 if "firebase" in p.name.lower() or "service" in p.name.lower() else 1, p.name))
                        auth = _init_from_service_account_path(preferred[0])
                        FIREBASE_ADMIN_INITIALIZED = True
                        logger.info("Initialized Firebase Admin from certs directory: %s", preferred[0])
            # If still not initialized, leave auth as None and fall through to dummy
    else:
        # already initialized earlier in same process
        auth = firebase_auth_module
        FIREBASE_ADMIN_INITIALIZED = True
        logger.info("Firebase Admin already initialized; using existing app.")

    # If we couldn't initialize, create a dummy auth object that raises explicit errors when used.
    if not FIREBASE_ADMIN_INITIALIZED:
        logger.warning("Firebase Admin not configured. Verification will fail until configured.")
        class _DummyAuth:
            def verify_id_token(self, token, **kwargs):
                raise RuntimeError(
                    "Firebase Admin SDK not configured. "
                    "Set FIREBASE_SERVICE_ACCOUNT_PATH or FIREBASE_SERVICE_ACCOUNT_JSON, "
                    "or set GOOGLE_APPLICATION_CREDENTIALS to your service account file."
                )
        auth = _DummyAuth()

except Exception as e:
    # Ensure import doesn't crash the app; log useful info.
    logger.exception("Failed to initialize Firebase Admin SDK: %s", e)
    class _DummyAuth:
        def verify_id_token(self, token, **kwargs):
            raise RuntimeError(f"Firebase Admin initialization failed: {e}")
    auth = _DummyAuth()


# Helpful wrapper to provide clearer errors to callers
def verify_id_token(id_token: str, check_revoked: bool = False):
    """
    Verify a Firebase ID token. Returns decoded token (dict) on success.
    Raises RuntimeError with a clear message on failure (so API can send 401).
    """
    if not id_token:
        raise RuntimeError("No ID token provided")

    try:
        # auth is either firebase_admin.auth (module) or a dummy with verify_id_token
        decoded = auth.verify_id_token(id_token, check_revoked=check_revoked)
        return decoded
    except firebase_exceptions.FirebaseError as fe:
        # firebase_admin specific exceptions (InvalidArgument, RevokedIdToken, etc.)
        logger.debug("FirebaseError during token verification: %s", fe)
        raise RuntimeError(f"Firebase token verification error: {fe}")
    except Exception as e:
        logger.debug("General exception during token verification: %s", e)
        raise RuntimeError(f"Invalid Firebase ID token: {e}")