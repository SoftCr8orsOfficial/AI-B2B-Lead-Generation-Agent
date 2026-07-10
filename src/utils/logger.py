"""
Logging Utility Module
Author: Muhammad Usman
Company: SoftCr8ors
"""

import logging
import os
from datetime import datetime
from src.config.config import Config

def setup_logger(name=__name__):
    """Setup and configure logger."""
    os.makedirs(Config.LOGS_DIR, exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        # File handler
        file_handler = logging.FileHandler(Config.LOG_FILE)
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger