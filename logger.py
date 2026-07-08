import logging
import sys
from pathlib import Path

def setup_logger(name: str = "coding_agent") -> logging.Logger:
    """Configures and returns a standardized, production-ready logger.
    
    Ensures that logs are cleanly formatted and outputs are streamed
    directly to the standard output device without creating duplicate handlers.
    """
    logger = logging.getLogger(name)
    
    # Prevent duplicate handlers if the logger is initialized multiple times
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Configure the standard output stream
        handler = logging.StreamHandler(sys.stdout)
        
        # Structure format: [Timestamp] LEVEL [Filename.Function:Line] Message
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # Prevent logs from propagating up to the root logger duplicate setups
        logger.propagate = False
        
    return logger

# Instantiated global singleton logger for the package
logger = setup_logger()