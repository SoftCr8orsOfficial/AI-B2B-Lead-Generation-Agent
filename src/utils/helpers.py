"""
Helper Utility Functions
Author: Muhammad Usman
Company: SoftCr8ors
"""

import re
import time
import random
from typing import Optional

def clean_text(text: str) -> str:
    """Clean and normalize text."""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_email(text: str) -> Optional[str]:
    """Extract email from text."""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(pattern, text)
    return match.group(0) if match else None

def extract_phone(text: str) -> Optional[str]:
    """Extract phone number from text."""
    pattern = r'\+?[\d\s\-\(\)]{8,20}'
    match = re.search(pattern, text)
    return match.group(0).strip() if match else None

def delay_request():
    """Add delay between requests."""
    time.sleep(random.uniform(1, 3))

def normalize_url(url: str) -> str:
    """Normalize URL."""
    if not url:
        return ""
    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url