"""
Configuration Module
Author: Muhammad Usman
Company: SoftCr8ors
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Directory paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
    PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
    EXPORTS_DIR = os.path.join(DATA_DIR, "exports")
    LOGS_DIR = os.path.join(BASE_DIR, "logs")
    
    # API Keys
    GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY", "")
    LINKEDIN_API_KEY = os.getenv("LINKEDIN_API_KEY", "")
    
    # Scraping settings
    REQUEST_TIMEOUT = 30
    REQUEST_DELAY = 2
    MAX_RETRIES = 3
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FILE = os.path.join(LOGS_DIR, "agent.log")