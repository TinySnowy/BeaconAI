import sys
import logging
from pathlib import Path
from loguru import logger
from app.core.config import settings

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

class InterceptHandler(logging.Handler):
    """
    Intercept standard logging messages and route them through loguru
    """
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where the logged message originated
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

def setup_logger():
    """Configure logger"""
    # Remove default handlers
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(logging.INFO)
    
    # Set logging levels for external libraries
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True
        
    # Configure loguru
    logger.configure(
        handlers=[
            {
                "sink": sys.stdout,
                "level": "DEBUG" if settings.DEBUG else "INFO",
                "format": "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
            },
            {
                "sink": "logs/beacon_ai.log",
                "rotation": "10 MB",
                "retention": "1 week",
                "level": "INFO",
                "format": "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}"
            }
        ]
    )
    
    return logger 