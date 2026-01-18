"""
Main entry point for Vercel deployment
Vercel looks for index.py in the root directory
"""
from app_vercel import app

# Vercel will use this app instance
# No need for if __name__ == '__main__' block
