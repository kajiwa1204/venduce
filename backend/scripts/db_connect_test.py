"""Diagnostic script to test psycopg2 connection behaviors with client encoding.

Run from repository backend virtualenv:

    python scripts/db_connect_test.py

It will try several approaches and print full tracebacks and exception args.
"""
import os
import sys
import traceback

# ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from app.db.database import DATABASE_URL
except Exception as e:
    print("Failed to import DATABASE_URL:", e)
    sys.exit(1)

print("DATABASE_URL:", DATABASE_URL)

TRIALS = [
    ("default", None, None),
    ("env-before-import-CP932", "CP932", None),
    ("env-before-import-UTF8", "UTF8", None),
    ("options-UTF8", None, "-c client_encoding=UTF8"),
    ("options-CP932", None, "-c client_encoding=CP932"),
]


def _remove_psycopg2_from_modules():
    # ensure a fresh import of psycopg2 for each trial
    for name in list(sys.modules.keys()):
        if name.startswith("psycopg2"):
            del sys.modules[name]


for name, env_val, options in TRIALS:
    print("\n--- Trial:", name, "---")
    if env_val is not None:
        os.environ["PGCLIENTENCODING"] = env_val
        print("Set PGCLIENTENCODING=", env_val)
    else:
        if "PGCLIENTENCODING" in os.environ:
            del os.environ["PGCLIENTENCODING"]
            print("Unset PGCLIENTENCODING")

    _remove_psycopg2_from_modules()

    try:
        import psycopg2
        print("psycopg2 version:", getattr(psycopg2, "__version__", "<no-version>"))
        if options:
            print("Connecting with options:", options)
            conn = psycopg2.connect(DATABASE_URL, options=options)
        else:
            print("Connecting with default options")
            conn = psycopg2.connect(DATABASE_URL)
        print("Connected OK")
        conn.close()
    except Exception as e:
        print("Exception type:", type(e))
        print("Exception repr:", repr(e))
        try:
            print("Exception args repr:", repr(e.args))
        except Exception:
            pass
        print("Full traceback:")
        traceback.print_exc()

print("\nDone tests.")
