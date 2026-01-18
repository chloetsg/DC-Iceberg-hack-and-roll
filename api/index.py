"""
Main entry point for Vercel deployment
"""
from app_vercel import app

# Vercel expects a handler
def handler(request):
    return app(request)
