import os
import logging 
from datetime import datetime
from dotenv import load_dotenv

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = CURRENT_DIR

load_dotenv()

API_KEY = os.getenv("NEWS_API_KEY")

if not API_KEY:
    print("⚠️  " + "=" * 50)
    print("⚠️  WARNING: NEWS_API_KEY not found!")
else:
    masked_key = API_KEY[:4] + "*" * (len(API_KEY) - 4)         #Masking and showing first 4 Characters
    print(f"✅ News API Key loaded: {masked_key}")

URL = 'https://newsapi.org'
API_TIMEOUT = 10