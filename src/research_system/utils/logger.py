import datetime
import logging
import os

# make the logs folder
LOGS_DIR = "logs"
os.makedirs(LOGS_DIR, exist_ok=True)

# make the log file
LOG_FILE = os.path.join(
    LOGS_DIR, f"log_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
)


# define the config
logging.basicConfig(
    filename=LOG_FILE,
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


def get_logger():
    """Returns the logger instance."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    return logger
