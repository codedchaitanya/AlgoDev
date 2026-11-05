"""Vercel entry point: serves the Django project (auth/wsgi.py) as a WSGI app."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from auth.wsgi import application as app  # noqa: E402
