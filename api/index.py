"""
Vercel Serverless Entrypoint
Exports Flask app for @vercel/python runtime.
"""
import os
import sys

# Add project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set VERCEL flag if not already set
os.environ.setdefault('VERCEL', '1')

from app import app

# Vercel looks for the WSGI application callable
application = app
