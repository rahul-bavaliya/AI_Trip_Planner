"""
logger.py — Reusable logger with colorful console output and detailed file logging.

Usage:
    from logger import get_logger

    log = get_logger(__name__)
    log.debug("Debug details")
    log.info("Server started")
    log.warning("Something looks off")
    log.error("Something failed")
    log.critical("Something is badly broken")
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler


class ColorFormatter(logging.Formatter):
    """Adds ANSI color codes to console log output based on level."""

    # ANSI escape codes
    GREY = "\x1b[38;20m"
    BLUE = "\x1b[34;20m"
    GREEN = "\x1b[32;20m"
    YELLOW = "\x1b[33;20m"
    RED = "\x1b[31;20m"
    BOLD_RED = "\x1b[31;1m"
    RESET = "\x1b[0m"

    BASE_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    LEVEL_COLORS = {
        logging.DEBUG: BLUE,
        logging.INFO: GREEN,
        logging.WARNING: YELLOW,
        logging.ERROR: RED,
        logging.CRITICAL: BOLD_RED,
    }

    def format(self, record):
        color = self.LEVEL_COLORS.get(record.levelno, self.GREY)
        fmt = f"{color}{self.BASE_FORMAT}{self.RESET}"
        formatter = logging.Formatter(fmt, datefmt=self.DATE_FORMAT)
        return formatter.format(record)


def get_logger(
    name: str = "app",
    log_dir: str = "logs",
    log_file: str = "app.log",
    console_level: int = logging.DEBUG,
    file_level: int = logging.DEBUG,
    max_bytes: int = 5 * 1024 * 1024,  # 5 MB per file
    backup_count: int = 5,
) -> logging.Logger:
    """
    Create (or fetch) a logger with:
      - Colorful, concise output to the console
      - Detailed, rotating file output on disk

    Args:
        name: Logger name (usually __name__ of the calling module)
        log_dir: Directory where log files are stored
        log_file: Log file name
        console_level: Minimum level shown in console
        file_level: Minimum level written to file
        max_bytes: Max size per log file before rotating
        backup_count: Number of rotated backup files to keep

    Returns:
        Configured logging.Logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # capture everything; handlers filter downstream

    # Avoid adding duplicate handlers if get_logger() is called multiple times
    if logger.handlers:
        return logger

    logger.propagate = False

    # --- Console handler (colorful, concise) ---
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(ColorFormatter())
    logger.addHandler(console_handler)

    # --- File handler (detailed, plain text, rotating) ---
    os.makedirs(log_dir, exist_ok=True)
    file_path = os.path.join(log_dir, log_file)

    file_handler = RotatingFileHandler(
        file_path, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
    )
    file_handler.setLevel(file_level)
    file_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | "
        "%(funcName)s() | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger