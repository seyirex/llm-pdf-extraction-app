"""
Logging utilities using Loguru.

Provides a centralized logger instance for the entire application.
"""

from loguru import logger
import sys
from pathlib import Path


def setup_logger(log_level: str = "INFO", log_file: str = "logs/app.log") -> None:
    """
    Configure the global logger instance.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file for persistent logging
    """
    logger.remove()
    
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True
    )
    
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=log_level,
        rotation="10 MB",
        retention="30 days",
        compression="zip"
    )


def get_logger():
    """
    Get the application logger instance.
    
    Returns:
        Loguru logger instance
    """
    return logger


setup_logger()
