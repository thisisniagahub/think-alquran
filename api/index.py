# Vercel Serverless Function Handler for FastAPI
# This file wraps the FastAPI app for Vercel deployment

import sys
import os
from pathlib import Path

# Add parent directory to path to import backend
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the FastAPI app from backend
from backend.server import app

# Create handler for Vercel
handler = app
