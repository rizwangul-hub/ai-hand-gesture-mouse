"""Logging utility for AI Hand Gesture Control System."""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler

def setup_logger(name: str = "HandMouse", log_file: str = "hand_mouse.log") -> logging.Logger:
    """Configure and return a standardized logger with console and rotating file output."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(threadName)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler
    try:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=3,
            encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as exc:
        print(f"Warning: Could not initialize file log handler: {exc}", file=sys.stderr)

    return logger

logger = setup_logger()
