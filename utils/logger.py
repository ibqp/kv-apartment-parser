import logging
from pathlib import Path
from datetime import datetime

# Project root
ROOT_DIR = Path(__file__).resolve().parent.parent

# Create logs directory if it doesn't exist
LOGS_DIR = ROOT_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# Logging settings
LOG_LEVEL = logging.DEBUG
LOG_FORMAT = '%(asctime)s - [%(levelname)s] - [%(filename)s:%(lineno)d] - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
MAX_LOG_FILES = 5 # max log files we want to keep


def cleanup_logs():
    """Clean up old log files. Keeps only the latest 'MAX_LOG_FILES'."""
    try:
        log_files = sorted(
            LOGS_DIR.glob("*.log")
            # , key=lambda f: f.stat().st_mtime # no need because logs have 'yyyymmddhhmmss' format
            , reverse=True
        )

        for old_log in log_files[MAX_LOG_FILES-1:]:
            old_log.unlink() # delete log
    except Exception as e:
        print(f"Error during log cleanup: {e}")


def setup_logger():
    """Setup logger with file and console handlers."""
    cleanup_logs() # clean up old logs before creating new one

    log_file = LOGS_DIR / f'{datetime.now().strftime("%Y%m%d%H%M%S")}.log'

    logging.basicConfig(
        level=LOG_LEVEL
        , format=LOG_FORMAT
        , datefmt=DATE_FORMAT
        , handlers=[
            logging.FileHandler(str(log_file)) # save to .log file
            , logging.StreamHandler() # output to the console
        ]
    )

    return logging.getLogger()
