import sys
import os
import io
import logging
from dotenv import load_dotenv
import importlib.util

# =====================================================
# FIX for OpenLiteSpeed / Passenger stdout/stderr fileno()
# =====================================================

class SafeStdout(io.TextIOWrapper):
    def fileno(self):
        return 1

class SafeStderr(io.TextIOWrapper):
    def fileno(self):
        return 2

if not hasattr(sys.stdout, "fileno"):
    sys.stdout = SafeStdout(sys.stdout.buffer, encoding="utf-8", errors="ignore")

if not hasattr(sys.stderr, "fileno"):
    sys.stderr = SafeStderr(sys.stderr.buffer, encoding="utf-8", errors="ignore")

# =====================================================
# BASIC CONFIG
# =====================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

load_dotenv(os.path.join(BASE_DIR, ".env"))

LOG_PATH = os.path.join(BASE_DIR, "passenger_startup.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler()
    ],
)

logging.info("Passenger start. BASE_DIR=%s", BASE_DIR)

# =====================================================
# LOAD FLASK APP EXPLICITLY
# =====================================================

def load_application():
    try:
        app_file = os.path.join(BASE_DIR, "app.py")
        logging.info("Loading explicit file: %s", app_file)

        spec = importlib.util.spec_from_file_location("app", app_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        app = module.app
        db = module.db

        with app.app_context():
            db.create_all()
            logging.info("db.create_all OK")

        logging.info("Loaded app.py successfully.")
        return app

    except Exception as e:
        logging.exception("Could not load app.py: %s", e)

        # ASCII ONLY - no utf8 characters!!
        def fallback(environ, start_response):
            start_response('500 Internal Server Error', [('Content-Type', 'text/plain')])
            return [b"Application load error - check passenger_startup.log"]

        return fallback

application = load_application()

logging.info("WSGI Application ready.")
