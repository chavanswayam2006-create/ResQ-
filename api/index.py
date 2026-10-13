"""
Vercel Serverless Function Entry Point for ResQ-Grid
Exposes WSGI 'app' object for @vercel/python runtime.
"""
import sys, os

# Add root repository directory to sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app import app

# Exported application callable for Vercel
app = app
